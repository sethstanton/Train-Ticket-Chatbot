// $(document).ready(function() {
//     // Function to retrieve the CSRF token from cookies
//     function getCsrfToken() {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 let cookie = cookies[i];
//                 while (cookie.charAt(0) === ' ') cookie = cookie.substring(1);
//                 if (cookie.indexOf('csrftoken=') == 0) {
//                     cookieValue = cookie.substring('csrftoken='.length, cookie.length);
//                 }
//             }
//         }
//         return cookieValue;
//     }

//     // Function to handle the unload event
//     function handleUnloadEvent() {
//         // Prepare the form data
//         let data = new URLSearchParams({
//             'csrfmiddlewaretoken': getCsrfToken(),
//             'confirm': 'true'
//         });

//         // Send the beacon
//         navigator.sendBeacon('/ticketfinder/clear_json/', data);
//     }

//     // Attach the event listener to beforeunload
//     window.addEventListener('beforeunload', handleUnloadEvent);
// });

