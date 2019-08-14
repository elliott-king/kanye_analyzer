import React from 'react';
import ReactDOM from 'react-dom';
import Select from 'react-select';

import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

import './static/style.css';
import './static/wavy-data.tar.gz';

function formatDate(datePosted) {
    let date = new Date(datePosted * 1000);
    let mo = (date.getMonth() + 1).toString().padStart(2, "0");
    let d = date.getDate().toString();
    let h = date.getHours().toString().padStart(2, "0");
    let mi = date.getMinutes().toString().padStart(2, "0");
    return `${mo}/${d} ${h}:${mi}`;
}

const positivityOptions = [
    {value: 'wavy', label: 'wavy'},
    {value: 'not_wavy', label: 'not wavy'},
];

const categoryOptions = [
    {value: 'poster', label: 'another poster on the subreddit'},
    {value: 'op', label: 'the original poster of the thread'},
    {value: 'link', label: 'the subject of the thread'},
    {value: 'this_sub', label: 'the r/kanye subreddit'},
    {value: 'external_person', label: 'an external individual'},
    {value: 'external_object', label: 'an external object'},
    {value: 'self', label: 'the user themselves'},
    {value: 'kanye', label: 'kanye himself'},
    {value: 'copypasta', label: 'nothing. It is a copypasta'},
    {value: 'misc', label: 'misc/other'},
]

class Comment extends React.Component{

    constructor(props) {
        super(props);
        this.state = {
            selectedCategory: null,
            selectedPositivity: null,
            date: formatDate(props.datePosted),
            submitButton: "Classify comment",
        };
    }

    handlePositivityChange(selectedOption) {
        this.setState({selectedPositivity: selectedOption});
    }

    handleCategoryChange(selectedOption){
        this.setState({selectedCategory: selectedOption});
    }

    handleSubmit(event) {
        event.preventDefault();
        var ret = {};
        if (this.state.selectedCategory) { ret['category'] = this.state.selectedCategory.value;}
        if (this.state.selectedPositivity) { ret['is_wavy'] = this.state.selectedPositivity.value;}
        if(Object.keys(ret).length === 0 && ret.constructor === Object) return;
        this.props.submitUserClassification(ret, this.props.commentId);
	this.setState({submitButton: "Done!"});
    }

    render() {
        return (
            <div className="comment-feed container" id={this.props.commentId} key={this.props.commentId}>
                <div className="row">
                    <p className="comment-author col">{this.props.author}</p>
                    <p className="comment-date col">{this.state.date}</p>
                </div>
                <div className="row">
                    <p className="comment-body col"><a href={this.props.link} target="_blank">{this.props.body}</a></p>
                </div>
                <div className="row classifications">
                    <div className="col returned-classifications">
                        <p className="row">This comment refers to: {this.props.categoryClassification}.</p>
                        <p className="row">And it is: {this.props.positivityClassification}.</p>
                    </div>
                    <form className="col classification-form" onSubmit={this.handleSubmit.bind(this)}>
                        <Select 
                            value={this.state.selectedCategory}
                            onChange={this.handleCategoryChange.bind(this)}
                            options={categoryOptions}
                            className="col"
                        />
                        <Select 
                            value={this.state.selectedPositivity}
                            onChange={this.handlePositivityChange.bind(this)}
                            options={positivityOptions}
                            className="col"
                        />
                        <button type="submit" className="btn">{this.state.submitButton}</button>
                    </form>
                </div>
            </div>
        );
    }
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
    
    submitUserClassification(classifications, commentId) {
        console.log(classifications, commentId);
        this.sock.emit('user_classification', classifications, commentId);
    }

	renderComment(commentId, author, datePosted, body, link, 
            positivityClassification, categoryClassification) {
		return (
			<Comment 
				key={commentId} 
				commentId={commentId} 
				author={author} 
				datePosted={datePosted} 
				body={body}
				link={link}
                submitUserClassification={this.submitUserClassification.bind(this)}
                categoryClassification={categoryClassification}
                positivityClassification={positivityClassification}/>
		);
	}

	render() {
		let commentArray = [];
        for (var i = this.state.commentQueue.length - 1; i >= 0; i--){ 
			var comment = this.state.commentQueue[i];
			commentArray.push(this.renderComment(
				comment.name, 
				comment.author, 
				comment.created_utc, 
				comment.body,
				"https://www.reddit.com" + comment.permalink,
                                comment.is_wavy,
                                comment.category));
		}
		return (
			<div className="comment-container container">
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

