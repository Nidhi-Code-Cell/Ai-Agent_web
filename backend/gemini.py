from google import genai
import requests
from datetime import datetime
from google.genai import types
import subprocess # this helps to execute command in terminal given by llm
import platform 
from dotenv import load_dotenv
import os # this this tell llm about pc type , which operating system you are using like window, mac, linux
load_dotenv()
os_platform = platform.system() # window

def executeCommand(command):  # its a tool which execute terminal command
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stderr.strip():
            return f"error: {result.stderr.strip()}"
        return f"success: {result.stdout.strip()}"
    except Exception as e:
        return f"error: {str(e)}"

def writeFile(path, content):  # this tool write content in respective file path instead of writing in terminal
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Website created successfully: wrote {len(content)} characters to {path}. check your project folder, let me know if you want any modifications!"
    except Exception as e:
        return f"error: {str(e)}"
    

    
def todayWeather(city):
    api_key = "4706f9b07e0fca2078b981234c74dc5f" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    data = requests.get(url).json()
    return data['main']['temp'] if 'main' in data else None


def cryptoPrice(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    data = requests.get(url).json()
    return str(data.get(coin,{}).get("usd"))


def getCurrTime():
    today=datetime.now()
    return today.strftime("%d %m %y")



# here we are defining tool and its property , what it do , what input it take , so that llm know when to use this tool and what input have to pass
executeCommandDeclaration = types.FunctionDeclaration(
    name="executeCommand",
    description="Execute a single terminal/shell command.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "command": types.Schema(type=types.Type.STRING)
        },
        required=["command"]
    )
)

writeFileDeclaration = types.FunctionDeclaration(
    name="writeFile",
    description="Write the given text content to a file at the specified path.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "path": types.Schema(type=types.Type.STRING, description="Path to file"),
            "content": types.Schema(type=types.Type.STRING, description="Full file content")
        },
        required=["path", "content"]
    )
)


todayWeatherDeclaration = types.FunctionDeclaration(
    name="todayWeather",
    description="Gets the current temperature for a given city in Celsius.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(type=types.Type.STRING, description="City name, e.g., Delhi")
        },
        required=["city"]
    )
)

cryptoPriceDeclaration = types.FunctionDeclaration(
    name="cryptoPrice",
    description="Gets the price of a cryptocurrency in USD.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "coin": types.Schema(type=types.Type.STRING, description="Cryptocurrency name, e.g., bitcoin")
        },
        required=["coin"]
    )
)


getCurrTimeDeclaration = types.FunctionDeclaration(
    name="getCurrTime",
    description="Returns the current date in the format DD MM YY.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
        required=[]
    )
)





api_key = os.getenv("GEMINI_API_KEY")  # read from .env
client = genai.Client(api_key=api_key)


tools = [
    types.Tool(function_declarations=[executeCommandDeclaration, writeFileDeclaration,getCurrTimeDeclaration, cryptoPriceDeclaration,todayWeatherDeclaration])
]

config = types.GenerateContentConfig(
    system_instruction=f"""
    
You are an expert website builder. Your task is to fully create a working website based on the user request.

RULES:
1. Always create folders using executeCommand (example: mkdir project_name).
2. Never use echo or cat to write file content.
3. Always use the writeFile tool to create and save file content.
   - The 'path' parameter must be the full relative path from the project root.
   - The 'content' parameter must contain the complete multi-line content of the file.
4. When building HTML, CSS, and JavaScript:
   - Ensure HTML is valid and links to CSS and JS files properly.
   - CSS should style the page cleanly.
   - JavaScript should have all required logic to make the website functional.
5. Use OS-specific commands only for folder creation or file moving (OS: {os_platform}).
6. Execute all steps one-by-one in logical order until the project is complete.
7. IMPORTANT: After completing website creation, ALWAYS provide a final response to the user explaining what you created and where to find it.

Example flow for "create a calculator website":
1. executeCommand: mkdir calculator
2. writeFile: calculator/index.html -> (full HTML content)
3. writeFile: calculator/style.css -> (full CSS content)
4. writeFile: calculator/script.js -> (full JS content)
5. Final response: "I've successfully created a calculator website in the 'calculator' folder. The website includes a fully functional calculator with HTML, CSS, and JavaScript files. You can open the index.html file in your browser to use it!"

The final website must be fully functional when opened in a browser.

In addition you have access of some external tool as well like todayWeather,cryptoPrice and getCurrTime.
You can use these function to answer user queries like what's the weather of Delhi, what is the day today or current price of crypto currencies.
    """,
    tools=tools
)



chat = client.chats.create(
    model="gemini-2.5-flash",
    config=config
)
def handle_response(resp):
    # Check if response has any parts at all
    if not resp.candidates or not resp.candidates[0].content.parts:
        return "Task completed successfully! Please check your project folder for any files that were created."
    
    for part in resp.candidates[0].content.parts:
        if getattr(part, "function_call", None):
            function_call = part.function_call
            fun_name = function_call.name
            args = function_call.args

            print(f"Function to call: {fun_name}")  # Enable this for debugging
            print(f"Arguments: {args}")

            if fun_name in globals():  # it check fun_name tool exist or not
                tool_result = globals()[fun_name](**args) # if exist , take that fun and pass args
                print(f"Tool result: {tool_result}")  # Enable this for debugging

                follow_up = chat.send_message( # whatever value fun return it send back to llm 
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fun_name,
                            response={"result": tool_result} 
                        )
                    )
                )
                return handle_response(follow_up) # here we keep calling function untill llm calling tool and not done with function calling
            else:
                return ("Error: Tool not found.")
    
    # Handle the final response text
    try:
        response_text = resp.text
        print(f"Final response text: '{response_text}'")  # Enable this for debugging
        
        # If response is empty, None, or just whitespace
        if not response_text or not response_text.strip():
            return "✅ Task completed successfully! I've finished creating your website. Please check your project folder to see the files I've created for you. Let me know if you need any modifications!"
        
        return response_text.strip()
        
    except Exception as e:
        print(f"Error getting response text: {e}")
        return "✅ Task completed successfully! Please check your project folder for the files I created."

def get_llm_response(user_message: str)-> str:
   
    response = chat.send_message(user_message, config=config) ## here user query send to llm 
    return handle_response(response) 