import React from 'react';
import ReactDOM from 'react-dom';
//import '../style.css';

function Comment(props) {
	return (
		<div className="comment" key={props.commentId}>
			<p className="comment-author">{props.author}</p>
			<p className="comment-date">{new Date(props.datePosted * 1000).toString()}</p>
			<p className="comment-body">{props.body}</p>
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

	renderComment(commentId, author, datePosted, body) {
		return (
			<Comment key={commentId} author={author} datePosted={datePosted} body={body}/>
		);
	}

	render() {
		let commentArray = [];
		for (var i = 0; i < this.state.commentQueue.length; i++){
			var comment = this.state.commentQueue[i];
			commentArray.push(this.renderComment(
				comment.name, 
				comment.author, 
				comment.created_utc, 
				comment.body));
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
		var newCommentQueue;

		// Limit queue to length 5
		if (this.state.commentQueue.length ===5) {
			newCommentQueue = this.state.commentQueue.slice(1);
		}
		else {
			newCommentQueue = this.state.commentQueue.slice();
		}

		newCommentQueue.push(comment);
		this.setState({commentQueue: newCommentQueue});
	}
}


// ReactDOM.render(
//   <Game />,
//     document.getElementById('root')
//     );
     
ReactDOM.render(
	<CommentContainer />,
	document.getElementById('realtime-container')
);
