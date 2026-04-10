document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');
    const printBtn = document.getElementById('print-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const sessionsList = document.getElementById('sessions-list');
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
    
    let chatHistory = [];
    let currentSessionId = null;
    let baseGreeting = null;

    // Load base greeting HTML
    const initialGreeting = chatMessages.firstElementChild;
    if (initialGreeting) {
        baseGreeting = initialGreeting.outerHTML;
    }

    // Initialize sessions
    loadSessions();

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value.trim() === '') {
            sendBtn.disabled = true;
        } else {
            sendBtn.disabled = false;
        }
    });

    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    const tasks = document.querySelectorAll('.task-tab');
    const durationSlider = document.getElementById('duration-slider');
    const durationValue = document.getElementById('duration-value');
    const generateBtn = document.getElementById('generate-btn');
    const controlPanel = document.getElementById('task-control-panel');
    const taskInstruction = document.getElementById('task-instruction');
    let currentTask = 'chat';

    // Handle Task Selection
    tasks.forEach(tab => {
        tab.addEventListener('click', () => {
            tasks.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTask = tab.dataset.task;
            
            // Toggle control panel visibility
            if (currentTask === 'chat' || currentTask === 'questions' || currentTask === 'remedial') {
                controlPanel.style.display = 'none';
                if (currentTask === 'chat') {
                    taskInstruction.textContent = 'اطرح أي سؤال حول المنهج للمناقشة والدردشة العامة';
                } else if (currentTask === 'questions') {
                    taskInstruction.textContent = 'اكتب موضوعاً لتوليد أسئلة احترافية حوله من المنهج';
                } else {
                    taskInstruction.textContent = 'اكتب موضوعاً لإعداد خطة علاجية وإثرائية شاملة';
                }
            } else {
                controlPanel.style.display = 'flex';
                taskInstruction.textContent = 'اختر المهمة التي تود إنجازها بناء على المنهج المعتمد';
                generateBtn.textContent = 'توليد خطة الدرس';
            }
        });
    });

    // Update Slider Value
    if (durationSlider) {
        durationSlider.addEventListener('input', (e) => {
            durationValue.textContent = e.target.value;
        });
    }

    // Generate Button Click
    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            const topic = userInput.value.trim();
            if (!topic) {
                alert('يرجى كتابة موضوع الدرس أولاً في مربع النص.');
                return;
            }
            
            let specialPrompt = "";
            const duration = durationSlider.value;

            if (currentTask === 'lesson_plan') {
                specialPrompt = `قم بإعداد خطة درس تفاعلية احترافية لموضوع: ${topic}. 
                مدة الحصة: ${duration} دقيقة.
                يجب أن تتضمن الخطة الأقسام التالية مع توزيع الوقت بدقة:
                I. الأهداف (Objectives): صياغة أهداف سلوكية واضحة.
                II. التمهيد (Introduction/Warm-up): مدته 5 دقائق، مع استراتيجية وإجراءات.
                III. سير الدرس (Lesson Flow): للمدة المتبقية، مقسماً لأنشطة (استكشاف، بناء مفهوم، تطبيق) مع استراتيجية ومفردات مستهدفة لكل نشاط.
                IV. التقييم الختامي (Concluding Assessment): لمدة 5 دقائق، مع استراتيجية Exit Ticket.
                استخدم لغة عربية رصينة وأسلوباً تربوياً حديثاً.`;
            } else if (currentTask === 'questions') {
                specialPrompt = `بناءً على المنهج المرفق، نفذ الطلب التالي بخصوص توليد الأسئلة: (${topic}). 
                التزم تماماً بنوع الأسئلة والعدد الذي طلبته، وإذا لم أحدد نوعاً فقم بتوليد تنوع احترافي (موضوعي ومقالي). 
                وضّح مستويات بلوم (Bloom's Taxonomy) لكل سؤال لتسهيل القياس التربوي.`;
            } else if (currentTask === 'remedial') {
                specialPrompt = `قم بإعداد خطة علاجية وإثرائية شاملة لموضوع: ${topic} بناءً على المنهج.`;
            }

            if (specialPrompt) {
                sendMessage(specialPrompt);
                userInput.value = '';
                userInput.style.height = 'auto';
            }
        });
    }

    async function sendMessage(overrideText = null) {
        // Handle cases where overrideText might be an Event object
        let message = (typeof overrideText === 'string') ? overrideText : userInput.value.trim();
        if (!message) return;

        // Automatically apply task-specific formatting if it's a direct user input (not from override)
        if (!overrideText) {
            if (currentTask === 'questions') {
                message = `بناءً على المنهج المرفق، نفذ الطلب التالي بخصوص توليد الأسئلة: (${message}). 
                التزم تماماً بنوع الأسئلة والعدد الذي طلبته، وإذا لم أحدد نوعاً فقم بتوليد تنوع احترافي (موضوعي ومقالي). 
                وضّح مستويات بلوم (Bloom's Taxonomy) لكل سؤال لتسهيل القياس التربوي.`;
            } else if (currentTask === 'remedial') {
                message = `قم بإعداد خطة علاجية وإثرائية شاملة لموضوع: ${message} بناءً على المنهج.`;
            } else if (currentTask === 'lesson_plan') {
                const duration = durationSlider.value;
                message = `قم بإعداد خطة درس تفاعلية احترافية لموضوع: ${message}. 
                مدة الحصة: ${duration} دقيقة.
                يجب أن تتضمن الخطة الأقسام التالية مع توزيع الوقت بدقة:
                I. الأهداف (Objectives): صياغة أهداف سلوكية واضحة.
                II. التمهيد (Introduction/Warm-up): مدته 5 دقائق، مع استراتيجية وإجراءات.
                III. سير الدرس (Lesson Flow): للمدة المتبقية، مقسماً لأنشطة (استكشاف، بناء مفهوم، تطبيق) مع استراتيجية ومفردات مستهدفة لكل نشاط.
                IV. التقييم الختامي (Concluding Assessment): لمدة 5 دقائق، مع استراتيجية Exit Ticket.
                استخدم لغة عربية رصينة وأسلوباً تربوياً حديثاً.`;
            }
        }

        // Add user message to UI
        appendMessage('user', message);
        chatHistory.push({ role: 'user', content: message });
        
        // Save or update session (use the first message as title for new sessions)
        saveCurrentSession(message);
        
        // Clear input field
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;

        // Show loading indicator
        const loadingId = showLoading();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    question: message, 
                    session_id: currentSessionId,
                    history: chatHistory.slice(0, -1) 
                })
            });

            const data = await response.json();
            
            // Remove loading indicator
            removeLoading(loadingId);

            if (data.error) {
                appendMessage('assistant', `**عذراً، حدث خطأ:** ${data.error}`);
            } else {
                appendMessage('assistant', data.answer);
                chatHistory.push({ role: 'assistant', content: data.answer });
                saveCurrentSession();
            }
            
        } catch (error) {
            removeLoading(loadingId);
            appendMessage('assistant', `**حدث خطأ:** فشل الاتصال بالخادم. تأكد من أن السيرفر يعمل بشكل صحيح.`);
        }
    }

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // If it's the assistant, we parse Markdown
        if (role === 'assistant') {
            bubble.innerHTML = marked.parse(text);
        } else {
            bubble.textContent = text;
        }
        
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function showLoading() {
        const id = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';
        loadingDiv.id = id;
        
        loadingDiv.innerHTML = `
            <div class="message-bubble loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        `;
        
        chatMessages.appendChild(loadingDiv);
        scrollToBottom();
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Initial disable of send btn
    sendBtn.disabled = true;

    // New Chat / Clear logic
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            startNewChat();
        });
    }

    // Print Logic
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }

    // Toggle Sidebar
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', () => {
            sidebar.classList.toggle('closed');
            const appLayout = document.querySelector('.app-layout');
            if (appLayout) {
                appLayout.classList.toggle('sidebar-open');
            }
        });
    }

    // Explicit Close Button (The definite fix)
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.add('closed');
            const appLayout = document.querySelector('.app-layout');
            if (appLayout) {
                appLayout.classList.remove('sidebar-open');
            }
        });
    }

    // Close sidebar when clicking backdrop (on mobile)
    const appLayout = document.querySelector('.app-layout');
    if (appLayout) {
        appLayout.addEventListener('click', (e) => {
            // If we click the layout (backdrop) itself, close the sidebar
            if (window.innerWidth <= 768 && e.target === appLayout && !sidebar.classList.contains('closed')) {
                sidebar.classList.add('closed');
                appLayout.classList.remove('sidebar-open');
            }
        });
    }

    // New Chat Button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }

    function startNewChat() {
        currentSessionId = null;
        chatHistory = [];
        chatMessages.innerHTML = baseGreeting || '';
        renderSessions(); // Remove active state
        
        // Visual feedback
        chatMessages.style.opacity = '0.5';
        setTimeout(() => chatMessages.style.opacity = '1', 200);
    }

    // Session Management (Local Storage)
    function getAllSessions() {
        const data = localStorage.getItem('physics_rag_sessions');
        return data ? JSON.parse(data) : [];
    }

    function saveCurrentSession(firstUserText = null) {
        if (chatHistory.length === 0) return;

        const sessions = getAllSessions();
        let session = sessions.find(s => s.id === currentSessionId);

        if (!session) {
            // Create new session
            currentSessionId = Date.now().toString();
            session = {
                id: currentSessionId,
                title: firstUserText ? firstUserText.substring(0, 30) + '...' : 'محادثة الجلسة',
                timestamp: Date.now(),
                history: []
            };
            sessions.unshift(session); // Add to top
        }

        session.history = chatHistory;
        localStorage.setItem('physics_rag_sessions', JSON.stringify(sessions));
        renderSessions();
    }

    function loadSession(id) {
        const sessions = getAllSessions();
        const session = sessions.find(s => s.id === id);
        if (session) {
            currentSessionId = session.id;
            chatHistory = session.history || [];
            
            // Re-render UI
            chatMessages.innerHTML = baseGreeting || '';
            chatHistory.forEach(msg => {
                appendMessage(msg.role, msg.content, true);
            });
            scrollToBottom();
            renderSessions();
            
            // On mobile, close sidebar after selection
            if (window.innerWidth <= 768) {
                sidebar.classList.add('closed');
            }
        }
    }

    function deleteSession(id) {
        let sessions = getAllSessions();
        sessions = sessions.filter(s => s.id !== id);
        localStorage.setItem('physics_rag_sessions', JSON.stringify(sessions));
        
        if (currentSessionId === id) {
            startNewChat();
        } else {
            renderSessions();
        }
    }

    function renameSession(id) {
        const sessions = getAllSessions();
        const session = sessions.find(s => s.id === id);
        if (!session) return;

        const newTitle = prompt('أدخل العنوان الجديد للمحادثة:', session.title);
        if (newTitle && newTitle.trim()) {
            session.title = newTitle.trim();
            localStorage.setItem('physics_rag_sessions', JSON.stringify(sessions));
            renderSessions();
        }
    }

    function loadSessions() {
        renderSessions();
        // Option to auto-load latest session? Left empty for now so they see greeting.
    }

    function renderSessions() {
        if (!sessionsList) return;
        const sessions = getAllSessions();
        sessionsList.innerHTML = '';
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<div style="color: rgba(255,255,255,0.4); text-align: center; padding: 20px; font-size: 0.9rem;">لا توجد محادثات سابقة</div>';
            return;
        }

        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = `session-item ${session.id === currentSessionId ? 'active' : ''}`;
            item.setAttribute('data-id', session.id);
            
            // Create title element
            const titleSpan = document.createElement('span');
            titleSpan.className = 'session-title';
            titleSpan.textContent = session.title;
            titleSpan.title = session.title;
            
            // Clicking the item (or title) loads the session
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.session-actions')) {
                    loadSession(session.id);
                }
            });
            
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'session-actions';

            const editBtn = document.createElement('button');
            editBtn.className = 'edit-session-btn';
            editBtn.innerHTML = '<i class="fas fa-edit"></i>'; // Better icon or text
            editBtn.textContent = '✎';
            editBtn.title = "تعديل العنوان";
            editBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                renameSession(session.id);
            };

            const delBtn = document.createElement('button');
            delBtn.className = 'delete-session-btn';
            delBtn.innerHTML = '×';
            delBtn.title = "حذف";
            delBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                deleteSession(session.id);
            };
            
            item.appendChild(titleSpan);
            actionsDiv.appendChild(editBtn);
            actionsDiv.appendChild(delBtn);
            item.appendChild(actionsDiv);
            sessionsList.appendChild(item);
        });
    }

    // Helper: modified appendMessage to skip formatting if from simple string in history
    function appendMessage(role, text, isHistoryLoad = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (role === 'assistant') {
            bubble.innerHTML = marked.parse(text);
        } else {
            bubble.textContent = text;
        }
        
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        if (!isHistoryLoad) scrollToBottom();
    }

});
