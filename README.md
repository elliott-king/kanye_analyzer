realtime.cannibaltaylor.com

# TODOS:
- Consider moving to python on the backend. (mostly done)

### High Priority:
- Better integrate python & node using rabbitMQ: https://medium.com/@HolmesLaurence/integrating-node-and-python-6b8454bfc272
- BACK UP MONGO

### Med Priority:
- In react-select for user classification, user should have a null option.
- Shuffle data before feeding into model.
- Retain mlp's vectorizer for use in classifying comments?
- Python server should be two servers! So they can run independently.
- Python server should restart upon code change.
- get_estimate in app.js has callback hell. Consider changing to request-promise-native
- Add "randomizer" button to main page, that will collect five random comments instead.

### Low priority:
- Refactor comment extraction - just get all comments from mongo, check if contains 'category' after.
- Move mlp to seperate dir w/in nlp/
- nlp.py feature extractor should have a more useful error if a comment does not have a specific key.
- Consider graphing change in accuracy w/ more test data: run several times & randomize each time, graph changes
- Reinforce (on client and server) that data is JSON format
- style.css is being duplicated (incl. @ index.jsx, also copies w/ webpack.config)
- Move to PostgreSQL?
- consider splitting the website and scraper
    a) Redis to communicate
    b) Postgres event notification
    c) Server-sent events: https://www.html5rocks.com/en/tutorials/eventsource/basics/#toc-js-api

