let isLoading = false;
        let chatMessages = [];

        // Auto-resize textarea
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });

        // Handle Enter key
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        }

        function startNewChat() {
            chatMessages = [];
            const chatContainer = document.getElementById('chatContainer');
            const welcomeScreen = document.getElementById('welcomeScreen');
            
            chatContainer.innerHTML = '';
            chatContainer.appendChild(welcomeScreen);
            
            // Close mobile sidebar
            document.getElementById('sidebar').classList.remove('open');
        }

        function sendExamplePrompt(prompt) {
            chatInput.value = prompt;
            sendMessage();
        }

        async function sendMessage() {
            const input = chatInput.value.trim();
            if (!input || isLoading) return;

            const sendButton = document.getElementById('sendButton');
            const chatContainer = document.getElementById('chatContainer');
            const welcomeScreen = document.getElementById('welcomeScreen');

            // Hide welcome screen if it's the first message
            if (welcomeScreen && welcomeScreen.parentNode) {
                welcomeScreen.remove();
            }
            // Add user message
            addMessage(input, 'user');
            chatInput.value = '';
            chatInput.style.height = 'auto';

            // Show loading state
            isLoading = true;
            sendButton.disabled = true;
            const loadingMessage = addLoadingMessage();

            try {
                const response = await fetch('http://127.0.0.1:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        userQuery: input
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                // Remove loading message
                loadingMessage.remove();
                
                // Add AI response
                addMessage(data.reply, 'ai');

            } catch (error) {
                console.error('Error:', error);
                
                // Remove loading message
                loadingMessage.remove();
                
                // Show error message
                addMessage(
                    "I apologize, but I'm having trouble connecting to the server. Please make sure the Flask server is running on http://127.0.0.1:5000 and try again.",
                    'ai',
                    true
                );
            } finally {
                isLoading = false;
                sendButton.disabled = false;
            }
        }

        function addMessage(content, type, isError = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;

            const avatar = document.createElement('div');
            avatar.className = `avatar ${type}-avatar`;
            avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            
            if (isError) {
                messageContent.innerHTML = `<div class="error-message">${content}</div>`;
            } else {
                // Handle different types of content
                if (typeof content === 'string') {
                    // Convert line breaks to HTML breaks for better formatting
                    const formattedContent = content.replace(/\n/g, '<br>');
                    messageContent.innerHTML = formattedContent;
                } else {
                    messageContent.textContent = String(content);
                }
            }

            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            chatContainer.appendChild(messageDiv);

            // Scroll to bottom smoothly
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 100);

            // Store message in conversation history
            chatMessages.push({ 
                type, 
                content: typeof content === 'string' ? content : String(content), 
                timestamp: new Date().toISOString(),
                id: Date.now() + Math.random() // Unique ID for each message
            });

            return messageDiv;
        }

        function addLoadingMessage() {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ai-message';

            const avatar = document.createElement('div');
            avatar.className = 'avatar ai-avatar';
            avatar.innerHTML = '<i class="fas fa-robot"></i>';

            const messageContent = document.createElement('div');
            messageContent.className = 'message-content loading';
            messageContent.innerHTML = `
                <span>AI is thinking</span>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;

            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            chatContainer.appendChild(messageDiv);

            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;

            return messageDiv;
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            const sidebar = document.getElementById('sidebar');
            const mobileToggle = document.querySelector('.mobile-toggle');
            
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                !mobileToggle.contains(e.target) && 
                sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        });

        // Focus input on load
        window.addEventListener('load', () => {
            chatInput.focus();
        });