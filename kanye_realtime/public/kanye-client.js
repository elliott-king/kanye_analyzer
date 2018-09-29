const sock = io();

divQueue = []
// queues in js: https://stackoverflow.com/questions/1590247/how-do-you-implement-a-stack-and-a-queue-in-javascript#1590262

function createDiv(comment_data) {
	// https://stackoverflow.com/questions/6840326/how-can-i-create-and-style-a-div-using-javascript
        var div = document.createElement("DIV");
        var fullname = comment_data.name;
        div.id = fullname;
        div.className = "individual-res";

	var user = document.createElement("P");
        user.className = "res-user";
        user.appendChild(document.createTextNode(comment_data.author));
        div.appendChild(user);

    var datePosted = document.createElement("P");
        datePosted.className = "res-date";
        // datePosted.appendChild(document.createTextNode(new Date()));
	    datePosted.appendChild(document.createTextNode(new Date(comment_data.created_utc * 1000)));
        div.appendChild(datePosted);

	var commentBody = document.createElement("P");
        commentBody.className = "res-comment";
        commentBody.appendChild(document.createTextNode(comment_data.body));
        div.appendChild(commentBody);
    return div;
}

function addComment(comment_data) {
	// First remove from queue & DOM if already five comments.

	console.log(comment_data); // Entire JSON, but more informative
	//console.log("Comment posted by: " + comment.data.author);
	//console.log("Contents: " + comment.data.body);

    if (divQueue.length === 5) {
		var oldestCommentFullname = divQueue.shift();
		var oldestCommentDiv = document.getElementById(oldestCommentFullname);
		oldestCommentDiv.parentNode.removeChild(oldestCommentDiv);
	}

	// Add to queue and DOM.
	var newCommentDiv = createDiv(comment_data);
	var fullname = comment_data.name;
	divQueue.push(fullname);

	var containerDiv = document.getElementById("realtime-container");
    console.log(containerDiv);
	containerDiv.appendChild(newCommentDiv);

}

sock.on('connect', () => {
    console.log('Socket.io connected');
});

sock.on('comment', (comment_data) => {
    addComment(JSON.parse(comment_data));
});
