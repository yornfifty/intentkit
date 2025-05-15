// --- Global Configuration ---
// Configure marked library once on load
if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true, // Convert single newlines to <br>
        gfm: true,    // Use GitHub Flavored Markdown
        // Optional: If you need further customization or face issues,
        // you might explore other options like 'pedantic: false'
    });
    console.log("Marked options set globally.");
} else {
    console.error("Marked library is not loaded. Markdown will not render correctly.");
}

// Global variables
let currentAgentId = null;
let currentChatId = null;
let selectedAgent = null;
let userAttachment = null;
let isServerOnline = false;
const LOCAL_STORAGE_KEY = 'agent_chats'; // Define key for local storage
let autoplayedAudioIds = new Set();

// DOM Elements
const agentsList = document.getElementById('agents-list');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const fileUpload = document.getElementById('file-upload');
const currentAgentElement = document.getElementById('current-agent');
const newChatButton = document.getElementById('new-chat-btn');
const chatSelector = document.getElementById('chat-selector');
const serverStatusModal = document.getElementById('server-status-modal');
const serverStatusMessage = document.getElementById('server-status-message');
const closeButtons = document.querySelectorAll('.close-button');
const skillCallModal = document.getElementById('skill-call-modal');
const skillId = document.getElementById('skill-id');
const skillName = document.getElementById('skill-name');
const skillParameters = document.getElementById('skill-parameters');
const skillResponse = document.getElementById('skill-response');

// --- Local Storage Functions ---

// Save chat information to local storage
function saveChatToStorage(agentId, chatId) {
    if (!agentId || !chatId) return;
    try {
        const savedChats = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || '{}');
        if (!savedChats[agentId]) {
            savedChats[agentId] = [];
        }
        // Add new chat ID only if it doesn't already exist
        if (!savedChats[agentId].includes(chatId)) {
            savedChats[agentId].push(chatId); // Add to the end (most recent)
        }
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(savedChats));
    } catch (error) {
        console.error("Failed to save chat to local storage:", error);
    }
}

// Load saved chats for a specific agent
function loadSavedChats(agentId) {
    if (!agentId) return [];
    try {
        const savedChats = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || '{}');
        return savedChats[agentId] || [];
    } catch (error) {
        console.error("Failed to load chats from local storage:", error);
        return []; // Return empty array on error
    }
}

// --- Core Logic ---

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch('http://localhost:8000', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.status >= 200 && response.status < 450) {
            isServerOnline = true;
            loadAgents();
            // Ensure controls are initially disabled until agent is selected
            disableChatControls();
        } else {
            isServerOnline = false;
            showServerStatusModal("The server is currently offline. Please check the server and try again.");
            disableChatControls();
        }
    } catch (error) {
        isServerOnline = false;
        showServerStatusModal("Could not connect to the server. Please make sure the server is running at http://localhost:8000");
        disableChatControls();
    }
}

// Load agents from API
async function loadAgents() {
    try {
        const response = await fetch('http://localhost:8000/agents');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const agents = await response.json();

        agentsList.innerHTML = ''; // Clear loading indicator

        if (agents && agents.length > 0) {
            agents.forEach(agent => {
                const agentElement = document.createElement('div');
                agentElement.className = 'agent-item';
                agentElement.dataset.id = agent.id;
                agentElement.innerHTML = `
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-description">${agent.description}</div>
                `;
                agentElement.addEventListener('click', () => selectAgent(agent));
                agentsList.appendChild(agentElement);
            });
        } else {
            agentsList.innerHTML = '<div class="loading-indicator">No agents available</div>';
        }
    } catch (error) {
        console.error("Failed to load agents:", error);
        agentsList.innerHTML = `<div class="loading-indicator">Failed to load agents: ${error.message}</div>`;
    }
}

// Select agent
function selectAgent(agent) {
    selectedAgent = agent;
    currentAgentId = agent.id;
    currentChatId = null; // Reset chat ID when switching agents

    // Update UI for selected agent
    document.querySelectorAll('.agent-item').forEach(item => item.classList.remove('selected'));
    const agentElement = document.querySelector(`.agent-item[data-id="${agent.id}"]`);
    if (agentElement) agentElement.classList.add('selected');
    currentAgentElement.textContent = agent.name;

    // Enable core chat controls now that an agent is selected
    newChatButton.disabled = false;
    chatSelector.disabled = false;

    // Load saved chats for this agent
    const agentChats = loadSavedChats(currentAgentId);

    // Populate chat selector
    populateChatSelector(agentChats);

    if (agentChats.length > 0) {
        // If chats exist, select the most recent one (last in the array)
        const latestChatId = agentChats[agentChats.length - 1];
        selectChat(latestChatId);
    } else {
        // If NO chats exist for this agent, create a new one automatically
        createNewChat();
    }
}

// Populate the chat selector dropdown
function populateChatSelector(chatIds) {
    chatSelector.innerHTML = '<option value="">Select a chat...</option>'; // Clear previous options
    if (!chatIds || chatIds.length === 0) {
        // If no chats, keep the selector disabled until a new chat is created
        // chatSelector.disabled = true; // Re-enabled when new chat is created
        return;
    }

    // chatSelector.disabled = false;
    chatIds.forEach((chatId, index) => {
        const option = document.createElement('option');
        option.value = chatId;
        // Display chat name based on its creation timestamp for easier identification
        const timestamp = chatId.split('_')[1];
        const chatDate = timestamp ? new Date(parseInt(timestamp)).toLocaleString() : `Chat ${index + 1}`;
        option.textContent = `Chat (${chatDate})`;
        chatSelector.appendChild(option);
    });
}

// Select a specific chat
function selectChat(chatId) {
    if (!currentAgentId || !chatId) return;

    currentChatId = chatId;
    chatSelector.value = chatId; // Update dropdown selection

    // Enable message input and send button
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.placeholder = "Type your message...";

    // Load the history for the selected chat
    loadChatHistory(currentAgentId, currentChatId);
}

// Create a new chat
function createNewChat() {
    if (!currentAgentId) return; // Need an agent selected first

    // Generate a unique chat ID using timestamp
    const newChatId = `chat_${Date.now()}`;
    currentChatId = newChatId; // Set the new chat as current

    // Save the new chat ID to local storage for the current agent
    saveChatToStorage(currentAgentId, newChatId);

    // Add the new chat to the selector
    const option = document.createElement('option');
    option.value = newChatId;
    const chatDate = new Date(parseInt(newChatId.split('_')[1])).toLocaleString();
    option.textContent = `Chat (${chatDate})`;
    chatSelector.appendChild(option); // Add to the end
    chatSelector.value = newChatId; // Select the new chat
    chatSelector.disabled = false; // Ensure selector is enabled

    // Clear messages area for the new chat
    chatMessages.innerHTML = '<div class="welcome-message"><p>New chat started. Send a message!</p></div>';

    // Enable input and focus
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.placeholder = "Type your message...";
    messageInput.focus();
}

// Load chat history
async function loadChatHistory(agentId, chatId) {
    if (!agentId || !chatId) {
        chatMessages.innerHTML = '<div class="welcome-message"><p>Select a chat to view messages.</p></div>';
        disableMessageInput(); // Disable input if no valid chat selected
        return;
    }

    chatMessages.innerHTML = '<div class="loading-indicator">Loading messages...</div>';
    messageInput.disabled = true; // Disable input while loading
    sendButton.disabled = true;

    try {
        const response = await fetch(`http://localhost:8000/agents/${agentId}/chat/history?chat_id=${chatId}&user_id=user1`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const messages = await response.json();

        chatMessages.innerHTML = ''; // Clear loading/previous messages

        if (messages && messages.length > 0) {
            // Call displayMessage with isNewMessage = false for historical messages
            messages.forEach(msg => displayMessage(msg, false)); // <--- MODIFIED
            chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
        } else {
            // Even if history is empty, show welcome for the active chat
            chatMessages.innerHTML = '<div class="welcome-message"><p>Start the conversation!</p></div>';
        }
        // Re-enable input now that history is loaded (or confirmed empty)
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.placeholder = "Type your message...";
        messageInput.focus();

    } catch (error) {
        console.error("Failed to load chat history:", error);
        chatMessages.innerHTML = `<div class="welcome-message"><p>Failed to load messages: ${error.message}. Please try again.</p></div>`;
        disableMessageInput(); // Disable input on error
    }
}

// Send message
async function sendMessage() {
    const messageText = messageInput.value.trim();
    if ((!messageText && !userAttachment) || !currentAgentId || !currentChatId) return;

    // --- Add User Message to UI (Optimistic Update) ---
    const userMessageData = {
        author_type: 'web',
        message: messageText,
        attachments: userAttachment ? [userAttachment] : [], // Show attachment immediately
        created_at: new Date().toISOString() // Use current time for immediate display
    };
    displayMessage(userMessageData, false); // User messages are never "new" for autoplay purpose

    // --- Prepare for API call ---
    const currentAttachment = userAttachment; // Capture attachment state for the API call
    userAttachment = null; // Reset global attachment variable
    messageInput.value = ''; // Clear input field
    messageInput.placeholder = "Type your message..."; // Reset placeholder

    // Add loading indicator for agent response
    const loadingElement = document.createElement('div');
    loadingElement.className = 'message-loading';
    loadingElement.innerHTML = `<div class="loading-dots"><span></span><span></span><span></span></div>`;
    chatMessages.appendChild(loadingElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom

    // Prepare API payload
    const payload = {
        chat_id: currentChatId,
        user_id: 'user1', // Replace with actual user management if needed
        message: messageText
    };
    if (currentAttachment) {
        payload.attachments = [currentAttachment];
        // IMPORTANT: If the attachment is a local file (Blob URL), the backend
        // won't be able to access it directly via the URL. You'd need a proper
        // file upload mechanism here in a real app before sending the message payload.
        // For this example, we assume the backend handles the attachment info correctly.
    }

    // --- Call API ---
    try {
        const response = await fetch(`http://localhost:8000/agents/${currentAgentId}/chat/v2`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // Always remove loading indicator regardless of success/error
        if (chatMessages.contains(loadingElement)) {
            chatMessages.removeChild(loadingElement);
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error sending message' }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        // --- Process Successful Response ---
        const agentReply = await response.json(); // Assuming API returns the new agent message object

        // Display the new agent message, marking it as new for potential autoplay
        // If the API returns an array of messages, loop through them:
        if (Array.isArray(agentReply)) {
            agentReply.forEach(msg => displayMessage(msg, true)); // <--- MODIFIED
        } else if (typeof agentReply === 'object' && agentReply !== null) {
            displayMessage(agentReply, true); // <--- MODIFIED (Handle single object response)
        } else {
            console.warn("Received unexpected response format from agent chat:", agentReply);
            // Optionally, reload history as a fallback if response isn't the message
            // await loadChatHistory(currentAgentId, currentChatId);
        }

        // --- REMOVED History Reload: We display the message directly ---
        // await loadChatHistory(currentAgentId, currentChatId);

        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to new message

    } catch (error) {
        console.error("Error sending message:", error);
        // Ensure loading indicator is removed on error as well
        if (chatMessages.contains(loadingElement)) {
            chatMessages.removeChild(loadingElement);
        }
        // Display error message in chat
        displayMessage({
            author_type: 'system', // Use a distinct type for system errors
            message: `Sorry, failed to send message: ${error.message}`,
            created_at: new Date().toISOString()
        }, false); // Errors don't autoplay
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    } finally {
        // Ensure input is re-enabled after API call attempt
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}


// Display message in chat
// function displayMessage(message) {
//     const messageElement = document.createElement('div');
//     let authorName = '';
//     let messageClass = '';

//     switch (message.author_type) {
//         case 'web':
//             messageClass = 'message-user';
//             authorName = 'You';
//             break;
//         case 'agent': // Corrected condition will target this
//             messageClass = 'message-agent';
//             authorName = selectedAgent?.name || 'Agent';
//             break;
//         case 'skill':
//             messageClass = 'message-skill'; // Use specific skill class
//             authorName = 'Skill';
//             break;
//         case 'system':
//             messageClass = 'message-system';
//             authorName = 'System';
//             break;
//         default:
//             messageClass = 'message-agent'; // Default to agent style
//             authorName = 'Unknown';
//     }

//     messageElement.className = `message ${messageClass}`;

//     let formattedMessage = message.message || '';
//     const mediaUrlsFromText = []; // Store media URLs found in markdown links
//     const attachmentContainer = document.createElement('div');
//     attachmentContainer.className = 'message-attachment';
//     const skillButtonContainer = document.createElement('div'); // Create container for skill buttons
//     skillButtonContainer.className = 'skill-button-container'; // Add class for styling


//     // --- Process Markdown Links First ---
//     const markdownLinkRegex = /\[([^\]]+?)\]\((https?:\/\/[^\s)]+)\)/g;
//     formattedMessage = formattedMessage.replace(markdownLinkRegex, (match, text, url) => {
//         if (message.author_type !== 'skill' && isMediaUrl(url)) {
//             if (!mediaUrlsFromText.includes(url)) {
//                 mediaUrlsFromText.push(url);
//             }
//         }
//         return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
//     });

//     // --- Optional: Process standalone URLs as well ---
//     const standaloneUrlRegex = /(?<!href=")(?<!src=")(https?:\/\/[^\s<]+)/g;
//     formattedMessage = formattedMessage.replace(standaloneUrlRegex, (match, url) => {
//         const cleanedUrl = url.replace(/[.!?)\];,]*$/, '');
//         if (message.author_type !== 'skill' && isMediaUrl(cleanedUrl)) {
//             if (!mediaUrlsFromText.includes(cleanedUrl)) {
//                 mediaUrlsFromText.push(cleanedUrl);
//             }
//             return `<a href="${cleanedUrl}" target="_blank" rel="noopener noreferrer">${cleanedUrl}</a>`;
//         }
//         return `<a href="${cleanedUrl}" target="_blank" rel="noopener noreferrer">${cleanedUrl}</a>`;
//     });


//     // --- Populate Attachment Container ---
//     // 1. Add previews from explicit message.attachments
//     if (message.attachments && message.attachments.length > 0) {
//         message.attachments.forEach(attachment => {
//             appendAttachmentElement(attachmentContainer, attachment); // Pass the container
//         });
//     }

//     // 2. Add previews from media URLs found in the text (only for non-skill messages)
//     if (message.author_type !== 'skill' && mediaUrlsFromText.length > 0) {
//         mediaUrlsFromText.forEach(url => {
//             const inferredType = inferMediaTypeFromUrl(url);
//             if (inferredType !== 'file') {
//                 const alreadyAdded = message.attachments?.some(att => att.url === url);
//                 if (!alreadyAdded) {
//                     appendAttachmentElement(attachmentContainer, { // Pass the container
//                         type: inferredType,
//                         url: url,
//                         name: url.substring(url.lastIndexOf('/') + 1)
//                     });
//                 }
//             }
//         });
//     }

//     // --- Construct the Message Element ---
//     messageElement.innerHTML = `
//         <div class="message-content">${formattedMessage}</div>
//         ${message.author_type !== 'system' ? `
//         <div class="message-meta">
//             <span>${authorName}</span>
//             <span>${new Date(message.created_at).toLocaleTimeString()}</span>
//         </div>` : ''}
//     `;

//     // Add skill call buttons if available (specifically for 'skill' type messages)
//     let hasSkillButtons = false;
//     if (message.skill_calls && message.skill_calls.length > 0 && message.author_type === 'skill') {
//         message.skill_calls.forEach(skillCall => {
//             const skillCallButton = document.createElement('button');
//             skillCallButton.className = 'skill-call-button';
//             skillCallButton.textContent = `View Skill: ${skillCall.name || 'Details'}`;
//             skillCallButton.addEventListener('click', (e) => {
//                 e.stopPropagation();
//                 showSkillCallModal(skillCall);
//             });
//             skillButtonContainer.appendChild(skillCallButton); // Add button to its container
//             hasSkillButtons = true;
//         });
//     }

//     // Append the skill button container *only if it has buttons*
//     if (hasSkillButtons) {
//         // Insert it after the meta info, or after content if no meta
//         const meta = messageElement.querySelector('.message-meta');
//         if (meta) {
//             meta.insertAdjacentElement('afterend', skillButtonContainer);
//         } else {
//             messageElement.querySelector('.message-content').insertAdjacentElement('afterend', skillButtonContainer);
//         }
//     }


//     // Append the attachment container *only if it has content*
//     if (attachmentContainer.hasChildNodes()) {
//         messageElement.appendChild(attachmentContainer);
//     }


//     // *** Add the completed message element to the DOM FIRST ***
//     chatMessages.appendChild(messageElement);

//     // *** THEN, attempt autoplay for any audio elements inside it ***
//     // *** CORRECTED CONDITION: Only autoplay AGENT messages ***
//     if (message.author_type === 'agent') { // <<<--- THIS LINE IS CHANGED
//         const audioElements = messageElement.querySelectorAll('audio'); // Find ALL audio elements in the message
//         audioElements.forEach(audioElement => {
//             // Check if it has an ID and hasn't been played this session
//             if (audioElement.id && !autoplayedAudioIds.has(audioElement.id)) {
//                 const audioId = audioElement.id; // Capture ID for use in promises/logs
//                 console.log(`Attempting to autoplay agent audio: ${audioId}`);
//                 // Attempt to play
//                 audioElement.play().then(() => {
//                     // Successfully started playing (or will play soon)
//                     autoplayedAudioIds.add(audioId); // Mark as played for this session
//                     console.log(`Autoplay started for agent audio: ${audioId}`);
//                 }).catch(error => {
//                     // Autoplay was prevented (common browser policy: needs user interaction first)
//                     console.warn(`Autoplay prevented for agent audio ${audioId}:`, error.message);
//                     // Add the ID even if prevented, so we don't keep trying/logging warnings for it
//                     autoplayedAudioIds.add(audioId);
//                 });
//             } else if (audioElement && !audioElement.id) {
//                 console.warn("Agent audio element found without an ID in message, cannot track for autoplay.");
//             }
//         });
//     }

//     // Scroll to the bottom after adding the message and potentially starting audio
//     chatMessages.scrollTop = chatMessages.scrollHeight;
// }
// Function name: displayMessage
// Full content:
// Function name: displayMessage
// Full content:
function displayMessage(message, isNewMessage = false) { // Added default for isNewMessage
    const messageElement = document.createElement('div');
    let authorName = '';
    let messageClass = '';

    // Determine message style and author based on author_type
    switch (message.author_type) {
        case 'web':
            messageClass = 'message-user';
            authorName = 'You';
            break;
        case 'agent':
            messageClass = 'message-agent';
            authorName = selectedAgent?.name || 'Agent';
            break;
        case 'skill':
            messageClass = 'message-skill'; // Use specific skill class
            authorName = 'Skill';
            break;
        case 'system':
            messageClass = 'message-system';
            authorName = 'System';
            break;
        default:
            messageClass = 'message-agent'; // Default to agent style
            authorName = 'Unknown';
    }

    messageElement.className = `message ${messageClass}`;

    // --- Prepare Containers ---
    const messageContentElement = document.createElement('div');
    messageContentElement.className = 'message-content';

    const attachmentContainer = document.createElement('div');
    attachmentContainer.className = 'message-attachment';

    const skillButtonContainer = document.createElement('div');
    skillButtonContainer.className = 'skill-button-container';

    // --- Process Message Text with Markdown and Sanitization ---
    const rawMessageText = message.message || '';
    try {
        // Marked options are now set globally, no need to set them here.

        // 1. Parse the raw text using Marked
        const unsafeHtml = marked.parse(rawMessageText);
        // console.log("Unsafe HTML (from marked):", unsafeHtml); // Optional debug log

        // 2. Sanitize the parsed HTML using DOMPurify
        //    Explicitly allow <br>, <strong>, and <em> tags to be safe.
        //    ADD_TAGS appends to the default allowed list.
        const safeHtml = DOMPurify.sanitize(unsafeHtml, {
            ADD_TAGS: ["br", "strong", "em"] // Ensure br and standard inline formatting are allowed
        });
        // console.log("Safe HTML (from DOMPurify):", safeHtml); // Optional debug log

        messageContentElement.innerHTML = safeHtml;

    } catch (error) {
        console.error("Error parsing or sanitizing Markdown:", error);
        // Fallback: Replace newlines with <br> even in fallback for consistency
        messageContentElement.innerHTML = rawMessageText.replace(/\n/g, '<br>');
    }

    // --- Process Attachments ---
    if (message.attachments && message.attachments.length > 0) {
        message.attachments.forEach(attachment => {
            // Use the existing helper function to append attachment elements
            appendAttachmentElement(attachmentContainer, attachment);
        });
    }

    // --- Add Skill Call Buttons (if applicable) ---
    let hasSkillButtons = false;
    if (message.skill_calls && message.skill_calls.length > 0 && message.author_type === 'skill') {
        message.skill_calls.forEach(skillCall => {
            const skillCallButton = document.createElement('button');
            skillCallButton.className = 'skill-call-button';
            skillCallButton.textContent = `View Skill: ${skillCall.name || 'Details'}`;
            skillCallButton.addEventListener('click', (e) => {
                e.stopPropagation();
                showSkillCallModal(skillCall);
            });
            skillButtonContainer.appendChild(skillCallButton); // Add button to its container
            hasSkillButtons = true;
        });
    }

    // --- Construct the Message Element ---
    // Start with the processed message content
    messageElement.appendChild(messageContentElement);

    // Add meta info (author, time), except for system messages
    if (message.author_type !== 'system') {
        const metaElement = document.createElement('div');
        metaElement.className = 'message-meta';
        metaElement.innerHTML = `
            <span>${authorName}</span>
            <span>${new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        `;
        messageElement.appendChild(metaElement);
    }

    // Add skill buttons container *if it has buttons*
    if (hasSkillButtons) {
        messageElement.appendChild(skillButtonContainer);
    }

    // Add attachment container *if it has content*
    if (attachmentContainer.hasChildNodes()) {
        messageElement.appendChild(attachmentContainer);
    }

    // *** Add the completed message element to the DOM FIRST ***
    chatMessages.appendChild(messageElement);

    // *** THEN, attempt autoplay for any audio elements inside it (only for AGENT messages) ***
    if (isNewMessage && message.author_type === 'agent') {
        const audioElements = messageElement.querySelectorAll('audio');
        audioElements.forEach(audioElement => {
            if (audioElement.id && !autoplayedAudioIds.has(audioElement.id)) {
                const audioId = audioElement.id;
                console.log(`Attempting to autoplay agent audio: ${audioId}`);
                audioElement.play().then(() => {
                    autoplayedAudioIds.add(audioId);
                    console.log(`Autoplay started for agent audio: ${audioId}`);
                }).catch(error => {
                    console.warn(`Autoplay prevented for agent audio ${audioId}:`, error.message);
                    autoplayedAudioIds.add(audioId); // Still add ID to prevent retry logs
                });
            } else if (audioElement && !audioElement.id) {
                console.warn("Agent audio element found without an ID in message, cannot track for autoplay.");
            }
        });
    }

    // Scroll to the bottom after adding the message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
// --- Helper Functions ---

// Helper to check if a URL likely points to media based on extension
function isMediaUrl(url) {
    if (!url || typeof url !== 'string') return false;
    // Basic check for common media extensions. Handles URLs with query parameters.
    return /\.(jpg|jpeg|png|gif|webp|bmp|svg|mp4|webm|ogg|mp3|wav|aac)(\?.*)?$/i.test(url);
}

// Helper to infer media type from URL extension
function inferMediaTypeFromUrl(url) {
    if (!url || typeof url !== 'string') return 'file';
    const extensionMatch = url.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg|mp4|webm|ogg|mp3|wav|aac)(\?.*)?$/i);
    if (!extensionMatch) return 'file';

    const ext = extensionMatch[1].toLowerCase();

    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(ext)) return 'image';
    if (['mp4', 'webm', 'ogg'].includes(ext)) return 'video'; // Note: ogg can be video or audio
    if (['mp3', 'wav', 'aac'].includes(ext)) return 'audio'; // Note: ogg can be audio

    return 'file'; // Default fallback
}


// Helper to append different attachment types to a container
// Function name: appendAttachmentElement
// Full content:
function appendAttachmentElement(container, attachment) {
    const url = attachment.url;
    // Infer type if not explicitly provided or is generic 'file'
    let type = attachment.type && attachment.type !== 'file' ? attachment.type : inferMediaTypeFromUrl(url);
    const name = attachment.name || (url ? url.split('/').pop() : 'Attachment'); // Use name or derive from URL
    const mimeType = attachment.mime_type; // Use provided mime type if available

    let elementHTML = '';
    const elementWrapper = document.createElement('div'); // Wrap each attachment
    elementWrapper.style.marginTop = '5px'; // Add a little space between multiple attachments

    // Only proceed if we have a URL
    if (!url) {
        // Handle case with no URL (maybe just text info?)
        elementHTML = `<div class="file-container"><div class="file-title">ℹ️ ${name || 'Attachment Info'}</div></div>`;
    } else if (type === 'image') {
        elementHTML = `<img src="${url}" alt="${name || 'Attachment Image'}" style="max-width: 300px; max-height: 250px; height: auto; border-radius: 8px; display: block;">`;
    } else if (type === 'video') {
        // Add preload="metadata" for better UX, remove autoplay attribute if present
        elementHTML = `<video controls preload="metadata" style="max-width: 300px; border-radius: 8px; display: block;"><source src="${url}" type="${mimeType || 'video/mp4'}"></video>`;
    } else if (type === 'audio') {
        // *** Add unique ID, keep controls and preload, NO autoplay attribute ***
        const audioId = `audio-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`; // Generate unique ID
        elementHTML = `<audio id="${audioId}" controls preload="metadata" style="width: 100%; max-width: 300px;"><source src="${url}" type="${mimeType || 'audio/mpeg'}"></audio>`;
    } else { // Generic file link fallback
        elementHTML = `
            <div class="file-container">
                <div class="file-title">📎 ${name || 'Attached File'}</div>
                <a href="${url}" target="_blank" rel="noopener noreferrer">Download/View File</a>
            </div>
        `;
    }

    elementWrapper.innerHTML = elementHTML;
    container.appendChild(elementWrapper);
}

// File upload handling
fileUpload.addEventListener('change', async function (e) {
    const file = e.target.files[0];
    if (!file || !currentAgentId) { // Need an agent selected to handle uploads conceptually
        e.target.value = null; // Reset file input
        return;
    };

    // For this demo, we immediately create a representation for the UI.
    // In a real app, you'd likely upload *first*, get a URL, then allow sending.
    // Here, we create a temporary object URL for local preview.

    const fileUrl = URL.createObjectURL(file); // Temporary local URL
    let fileType = file.type.split('/')[0];
    if (!['image', 'video', 'audio'].includes(fileType)) {
        fileType = 'file'; // Categorize others as generic file
    }

    userAttachment = {
        type: fileType,
        url: fileUrl, // Use the temporary URL for display
        name: file.name,
        mime_type: file.type // Store mime type
        // In a real scenario, after upload, replace 'url' with the persistent server URL
        // You might also add file size, etc.
    };

    // Show indication that a file is attached
    messageInput.placeholder = `Attached: ${file.name} (Type message or just send)`;
    // Optionally display a preview thumbnail near the input? (More complex UI)

    e.target.value = null; // Reset file input to allow selecting the same file again
});

// Show server status modal
function showServerStatusModal(message) {
    serverStatusMessage.textContent = message;
    serverStatusModal.style.display = 'flex';
}

// Show skill call details
function showSkillCallModal(skillCall) {
    // Get references to the modal elements
    const modal = document.getElementById('skill-call-modal');
    const idElement = document.getElementById('skill-id');
    const nameElement = document.getElementById('skill-name');
    const paramsPreElement = document.getElementById('skill-parameters');
    const responseTextElement = document.getElementById('skill-response-text');
    const mediaPreviewElement = document.getElementById('skill-response-media');
    const mediaSectionElement = document.getElementById('skill-media-section');

    // --- Reset previous content ---
    idElement.textContent = '';
    nameElement.textContent = '';
    paramsPreElement.textContent = '';
    responseTextElement.innerHTML = ''; // Use innerHTML to allow inserting <pre> or text
    mediaPreviewElement.innerHTML = '';
    mediaSectionElement.style.display = 'none'; // Hide media section initially

    // --- Populate Basic Info ---
    idElement.textContent = skillCall.id || 'N/A';
    nameElement.textContent = skillCall.name || 'N/A';

    // --- Format and Populate Parameters ---
    try {
        // Ensure parameters is an object/array before stringifying if needed
        const paramsData = typeof skillCall.parameters === 'string'
            ? JSON.parse(skillCall.parameters)
            : skillCall.parameters;

        // Beautify the JSON parameters
        paramsPreElement.textContent = JSON.stringify(paramsData || {}, null, 2); // Use 2 spaces for indentation
    } catch (e) {
        console.error("Error parsing/formatting skill parameters:", e);
        // Fallback: Display as string if parsing/stringifying fails
        paramsPreElement.textContent = String(skillCall.parameters || 'Invalid Parameter Format');
    }

    // --- Process and Populate Response ---
    const responseData = skillCall.response;
    let mediaUrl = null; // Variable to store a detected media URL

    try {
        let isJson = false;
        let parsedResponse;

        // Attempt to parse if it's a string
        if (typeof responseData === 'string') {
            try {
                parsedResponse = JSON.parse(responseData);
                isJson = true;
            } catch (e) {
                // Not JSON, treat as plain text
                isJson = false;
            }
        } else if (typeof responseData === 'object' && responseData !== null) {
            // Already an object/array
            parsedResponse = responseData;
            isJson = true;
        }

        // Display the raw response (formatted if JSON)
        if (isJson) {
            // Create a <pre> element for formatted JSON
            const pre = document.createElement('pre');
            pre.textContent = JSON.stringify(parsedResponse, null, 2);
            responseTextElement.appendChild(pre);

            // Check common JSON structures for media URLs
            if (parsedResponse?.image_url && typeof parsedResponse.image_url === 'string') {
                mediaUrl = parsedResponse.image_url;
            } else if (parsedResponse?.data && Array.isArray(parsedResponse.data) && parsedResponse.data[0]?.url && typeof parsedResponse.data[0].url === 'string') {
                mediaUrl = parsedResponse.data[0].url; // Handle DALL-E like structure
            } else if (parsedResponse?.url && typeof parsedResponse.url === 'string' && isMediaUrl(parsedResponse.url)) {
                mediaUrl = parsedResponse.url; // If the JSON itself has a top-level media url
            }

        } else {
            // Display as plain text in a div
            const div = document.createElement('div');
            div.textContent = String(responseData ?? ''); // Handle null/undefined
            responseTextElement.appendChild(div);

            // Check if the plain text string itself is a media URL
            if (typeof responseData === 'string' && isMediaUrl(responseData)) {
                mediaUrl = responseData;
            }
        }

    } catch (error) {
        console.error("Error processing skill response:", error);
        // Fallback display in case of unexpected errors
        const div = document.createElement('div');
        div.textContent = `Error displaying response: ${error}\n\nRaw: ${String(responseData ?? '')}`;
        responseTextElement.appendChild(div);
    }

    // --- Generate Media Preview (if mediaUrl was found) ---
    if (mediaUrl) {
        const mediaType = inferMediaTypeFromUrl(mediaUrl);
        let previewHTML = '';

        if (mediaType === 'image') {
            previewHTML = `<img src="${mediaUrl}" alt="Skill Response Media Preview">`;
        } else if (mediaType === 'video') {
            previewHTML = `<video controls preload="metadata"><source src="${mediaUrl}"></video>`;
        } else if (mediaType === 'audio') {
            previewHTML = `<audio controls preload="metadata"><source src="${mediaUrl}"></audio>`;
        } else {
            // If it's a URL but not recognized media, provide a link
            previewHTML = `<a href="${mediaUrl}" target="_blank" rel="noopener noreferrer">View Resource Link</a>`;
        }

        if (previewHTML) {
            mediaPreviewElement.innerHTML = previewHTML;
            mediaSectionElement.style.display = 'block'; // Show the media section
        }
    }

    // --- Display the Modal ---
    modal.style.display = 'flex';
}


// --- UI Helper Functions ---

function disableChatControls() {
    messageInput.disabled = true;
    sendButton.disabled = true;
    newChatButton.disabled = true;
    chatSelector.disabled = true;
    messageInput.placeholder = "Select an agent to start";
    chatSelector.innerHTML = '<option value="">Select agent first</option>'; // Clear selector
    currentAgentElement.textContent = 'Select an agent';
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>Welcome to Agent Chat</h2>
            <p>Select an agent from the sidebar to start a conversation.</p>
            ${!isServerOnline ? '<p style="color: #ff6b6b;">Server appears offline.</p>' : ''}
        </div>`;
}

function disableMessageInput() {
    messageInput.disabled = true;
    sendButton.disabled = true;
    messageInput.placeholder = "Select a chat or create a new one";
}


// --- Event Listeners ---

window.addEventListener('DOMContentLoaded', () => {
    checkServerStatus(); // Check status and load agents on start
});

// Close modal buttons
closeButtons.forEach(button => {
    button.addEventListener('click', function () {
        this.closest('.modal').style.display = 'none';
    });
});

// Close modals when clicking outside content
window.addEventListener('click', (event) => {
    if (event.target === serverStatusModal) {
        serverStatusModal.style.display = 'none';
    }
    if (event.target === skillCallModal) {
        skillCallModal.style.display = 'none';
    }
});

// Send message button
sendButton.addEventListener('click', sendMessage);

// Send message on Enter key (allow Shift+Enter for newline)
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Prevent newline
        if (!sendButton.disabled) { // Check if sending is allowed
            sendMessage();
        }
    }
});

// New chat button
newChatButton.addEventListener('click', createNewChat);

// Chat selector change
chatSelector.addEventListener('change', () => {
    const selectedChatId = chatSelector.value;
    if (selectedChatId) {
        selectChat(selectedChatId); // Load selected chat history
    } else {
        // Handle the "Select a chat..." option being chosen
        currentChatId = null;
        chatMessages.innerHTML = '<div class="welcome-message"><p>Select a chat from the list above or create a new one.</p></div>';
        disableMessageInput();
    }
});

// Ensure attachment label works
document.querySelector('.attachment-label').addEventListener('click', () => {
    if (!messageInput.disabled) { // Only allow attachment if input is enabled
        fileUpload.click();
    }
});