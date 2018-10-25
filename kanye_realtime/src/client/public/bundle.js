/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/client/app/kanye-client.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/client/app/kanye-client.js":
/*!****************************************!*\
  !*** ./src/client/app/kanye-client.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("const sock = io();\n\ndivQueue = []\n// queues in js: https://stackoverflow.com/questions/1590247/how-do-you-implement-a-stack-and-a-queue-in-javascript#1590262\n\nfunction createDiv(comment_data) {\n\t// https://stackoverflow.com/questions/6840326/how-can-i-create-and-style-a-div-using-javascript\n        var div = document.createElement(\"DIV\");\n        var fullname = comment_data.name;\n        div.id = fullname;\n        div.className = \"individual-res\";\n\n\tvar user = document.createElement(\"P\");\n        user.className = \"res-user\";\n        user.appendChild(document.createTextNode(comment_data.author));\n        div.appendChild(user);\n\n    var datePosted = document.createElement(\"P\");\n        datePosted.className = \"res-date\";\n        // datePosted.appendChild(document.createTextNode(new Date()));\n\t    datePosted.appendChild(document.createTextNode(new Date(comment_data.created_utc * 1000)));\n        div.appendChild(datePosted);\n\n\tvar commentBody = document.createElement(\"P\");\n        commentBody.className = \"res-comment\";\n        commentBody.appendChild(document.createTextNode(comment_data.body));\n        div.appendChild(commentBody);\n    return div;\n}\n\nfunction addComment(comment_data) {\n\t// First remove from queue & DOM if already five comments.\n\n\tconsole.log(comment_data); // Entire JSON, but more informative\n\t//console.log(\"Comment posted by: \" + comment.data.author);\n\t//console.log(\"Contents: \" + comment.data.body);\n\n    if (divQueue.length === 5) {\n\t\tvar oldestCommentFullname = divQueue.shift();\n\t\tvar oldestCommentDiv = document.getElementById(oldestCommentFullname);\n\t\toldestCommentDiv.parentNode.removeChild(oldestCommentDiv);\n\t}\n\n\t// Add to queue and DOM.\n\tvar newCommentDiv = createDiv(comment_data);\n\tvar fullname = comment_data.name;\n\tdivQueue.push(fullname);\n\n\tvar containerDiv = document.getElementById(\"realtime-container\");\n    console.log(containerDiv);\n\tcontainerDiv.appendChild(newCommentDiv);\n\n}\n\nsock.on('connect', () => {\n    console.log('Socket.io connected');\n});\n\nsock.on('comment', (comment_data) => {\n    addComment(JSON.parse(comment_data));\n});\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY2xpZW50L2FwcC9rYW55ZS1jbGllbnQuanMuanMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9zcmMvY2xpZW50L2FwcC9rYW55ZS1jbGllbnQuanM/MjkwNyJdLCJzb3VyY2VzQ29udGVudCI6WyJjb25zdCBzb2NrID0gaW8oKTtcblxuZGl2UXVldWUgPSBbXVxuLy8gcXVldWVzIGluIGpzOiBodHRwczovL3N0YWNrb3ZlcmZsb3cuY29tL3F1ZXN0aW9ucy8xNTkwMjQ3L2hvdy1kby15b3UtaW1wbGVtZW50LWEtc3RhY2stYW5kLWEtcXVldWUtaW4tamF2YXNjcmlwdCMxNTkwMjYyXG5cbmZ1bmN0aW9uIGNyZWF0ZURpdihjb21tZW50X2RhdGEpIHtcblx0Ly8gaHR0cHM6Ly9zdGFja292ZXJmbG93LmNvbS9xdWVzdGlvbnMvNjg0MDMyNi9ob3ctY2FuLWktY3JlYXRlLWFuZC1zdHlsZS1hLWRpdi11c2luZy1qYXZhc2NyaXB0XG4gICAgICAgIHZhciBkaXYgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KFwiRElWXCIpO1xuICAgICAgICB2YXIgZnVsbG5hbWUgPSBjb21tZW50X2RhdGEubmFtZTtcbiAgICAgICAgZGl2LmlkID0gZnVsbG5hbWU7XG4gICAgICAgIGRpdi5jbGFzc05hbWUgPSBcImluZGl2aWR1YWwtcmVzXCI7XG5cblx0dmFyIHVzZXIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KFwiUFwiKTtcbiAgICAgICAgdXNlci5jbGFzc05hbWUgPSBcInJlcy11c2VyXCI7XG4gICAgICAgIHVzZXIuYXBwZW5kQ2hpbGQoZG9jdW1lbnQuY3JlYXRlVGV4dE5vZGUoY29tbWVudF9kYXRhLmF1dGhvcikpO1xuICAgICAgICBkaXYuYXBwZW5kQ2hpbGQodXNlcik7XG5cbiAgICB2YXIgZGF0ZVBvc3RlZCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoXCJQXCIpO1xuICAgICAgICBkYXRlUG9zdGVkLmNsYXNzTmFtZSA9IFwicmVzLWRhdGVcIjtcbiAgICAgICAgLy8gZGF0ZVBvc3RlZC5hcHBlbmRDaGlsZChkb2N1bWVudC5jcmVhdGVUZXh0Tm9kZShuZXcgRGF0ZSgpKSk7XG5cdCAgICBkYXRlUG9zdGVkLmFwcGVuZENoaWxkKGRvY3VtZW50LmNyZWF0ZVRleHROb2RlKG5ldyBEYXRlKGNvbW1lbnRfZGF0YS5jcmVhdGVkX3V0YyAqIDEwMDApKSk7XG4gICAgICAgIGRpdi5hcHBlbmRDaGlsZChkYXRlUG9zdGVkKTtcblxuXHR2YXIgY29tbWVudEJvZHkgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KFwiUFwiKTtcbiAgICAgICAgY29tbWVudEJvZHkuY2xhc3NOYW1lID0gXCJyZXMtY29tbWVudFwiO1xuICAgICAgICBjb21tZW50Qm9keS5hcHBlbmRDaGlsZChkb2N1bWVudC5jcmVhdGVUZXh0Tm9kZShjb21tZW50X2RhdGEuYm9keSkpO1xuICAgICAgICBkaXYuYXBwZW5kQ2hpbGQoY29tbWVudEJvZHkpO1xuICAgIHJldHVybiBkaXY7XG59XG5cbmZ1bmN0aW9uIGFkZENvbW1lbnQoY29tbWVudF9kYXRhKSB7XG5cdC8vIEZpcnN0IHJlbW92ZSBmcm9tIHF1ZXVlICYgRE9NIGlmIGFscmVhZHkgZml2ZSBjb21tZW50cy5cblxuXHRjb25zb2xlLmxvZyhjb21tZW50X2RhdGEpOyAvLyBFbnRpcmUgSlNPTiwgYnV0IG1vcmUgaW5mb3JtYXRpdmVcblx0Ly9jb25zb2xlLmxvZyhcIkNvbW1lbnQgcG9zdGVkIGJ5OiBcIiArIGNvbW1lbnQuZGF0YS5hdXRob3IpO1xuXHQvL2NvbnNvbGUubG9nKFwiQ29udGVudHM6IFwiICsgY29tbWVudC5kYXRhLmJvZHkpO1xuXG4gICAgaWYgKGRpdlF1ZXVlLmxlbmd0aCA9PT0gNSkge1xuXHRcdHZhciBvbGRlc3RDb21tZW50RnVsbG5hbWUgPSBkaXZRdWV1ZS5zaGlmdCgpO1xuXHRcdHZhciBvbGRlc3RDb21tZW50RGl2ID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQob2xkZXN0Q29tbWVudEZ1bGxuYW1lKTtcblx0XHRvbGRlc3RDb21tZW50RGl2LnBhcmVudE5vZGUucmVtb3ZlQ2hpbGQob2xkZXN0Q29tbWVudERpdik7XG5cdH1cblxuXHQvLyBBZGQgdG8gcXVldWUgYW5kIERPTS5cblx0dmFyIG5ld0NvbW1lbnREaXYgPSBjcmVhdGVEaXYoY29tbWVudF9kYXRhKTtcblx0dmFyIGZ1bGxuYW1lID0gY29tbWVudF9kYXRhLm5hbWU7XG5cdGRpdlF1ZXVlLnB1c2goZnVsbG5hbWUpO1xuXG5cdHZhciBjb250YWluZXJEaXYgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChcInJlYWx0aW1lLWNvbnRhaW5lclwiKTtcbiAgICBjb25zb2xlLmxvZyhjb250YWluZXJEaXYpO1xuXHRjb250YWluZXJEaXYuYXBwZW5kQ2hpbGQobmV3Q29tbWVudERpdik7XG5cbn1cblxuc29jay5vbignY29ubmVjdCcsICgpID0+IHtcbiAgICBjb25zb2xlLmxvZygnU29ja2V0LmlvIGNvbm5lY3RlZCcpO1xufSk7XG5cbnNvY2sub24oJ2NvbW1lbnQnLCAoY29tbWVudF9kYXRhKSA9PiB7XG4gICAgYWRkQ29tbWVudChKU09OLnBhcnNlKGNvbW1lbnRfZGF0YSkpO1xufSk7XG4iXSwibWFwcGluZ3MiOiJBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOyIsInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/client/app/kanye-client.js\n");

/***/ })

/******/ });