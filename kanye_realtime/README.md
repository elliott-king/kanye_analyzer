# TODOS:
- Consider moving to python on the backend.

### High Priority:
- Better integrate python & node using rabbitMQ: https://medium.com/@HolmesLaurence/integrating-node-and-python-6b8454bfc272
- BACK UP MONGO

### Med Priority:
- In react select for user classification, user should have a null option.
- Shuffle data before feeding into model.
- Retain mlp's vectorizer for use in classifying comments?
- Move mlp to seperate dir w/in nlp/
- Consider graphing change in accuracy w/ more test data: run several times & randomize each time, graph changes
- Python server should be two servers! So they can run independently.
- Python server should restart upon code change.
- async nature of 'get_estimate' in app.js causes comments to not return to frontend in order (should just call for multiple comments @ once, then return answers for all in one go).
- Refactor comment extraction - just get all comments from mongo, check if contains 'category' after.

### Low priority:
- When user submits classification, button should change 'submit' -> 'thanks!'
- nlp.py feature extractor should have a more useful error if a comment does not have a specific key.
- Reinforce (on client and server) that data is JSON format
- style.css is being duplicated (incl. @ index.jsx, also copies w/ webpack.config)
- Move to PostgreSQL?
- consider splitting the website and scraper
    a) Redis to communicate
    b) Postgres event notification
    c) Server-sent events: https://www.html5rocks.com/en/tutorials/eventsource/basics/#toc-js-api

