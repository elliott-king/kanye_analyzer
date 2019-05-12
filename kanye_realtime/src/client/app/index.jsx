import React from 'react';
import ReactDOM from 'react-dom';
//import '../style.css';

function Comment(props) {
    let date = new Date(props.datePosted * 1000);
    date = `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getDate()} \
${date.getHours()}:${date.getMinutes()}`;
	return (
		<div className="comment" id={props.commentId} key={props.commentId}>
			<p className="comment-author">{props.author}</p>
			<p className="comment-date">{date}</p>
			<p className="comment-body"><a href={props.link}>{props.body}</a></p>
		</div>
	);
}

class CommentContainer extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			commentQueue: []
		};

		// Handle incoming messages.
		this.sock = io();
		this.sock.on('connect', () => {
			console.log('Connected to server');
		});
		this.sock.on('comment', (comment) => {
			this.addComment(JSON.parse(comment));
		});
	}

	renderComment(commentId, author, datePosted, body, link) {
		return (
			<Comment 
				key={commentId} 
				commentId={commentId} 
				author={author} 
				datePosted={datePosted} 
				body={body}
				link={link}/>
		);
	}

	render() {
		let commentArray = [];
        for (var i = this.state.commentQueue.length - 1; i >= 0; i--){ 
//		for (var i = 0; i < this.state.commentQueue.length; i++){
			var comment = this.state.commentQueue[i];
			commentArray.push(this.renderComment(
				comment.name, 
				comment.author, 
				comment.created_utc, 
				comment.body,
				"https://www.reddit.com" + comment.permalink));
		}
		return (
			<div className="comment-container">
				{commentArray}
			</div>
		)
	}

	// TODO: hacky
	addComment(comment) {

		// Keep immutable for React
		var newCommentQueue = this.state.commentQueue.slice();

		// Limit queue to length 5
		while (newCommentQueue.length >= 5) {
			newCommentQueue.shift();
		}

		newCommentQueue.push(comment);
		this.setState({commentQueue: newCommentQueue});
	}
}
     
ReactDOM.render(
	<CommentContainer />,
	document.getElementById('realtime-container')
);

