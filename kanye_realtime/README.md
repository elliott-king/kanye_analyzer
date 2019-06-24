# TODOS:
- Consider moving to python on the backend.

### High Priority:
- Rerun python model every so often (taking into account user classification).
- Change nlp classifier based on given input.
- Better integrate python & node using rabbitMQ: https://medium.com/@HolmesLaurence/integrating-node-and-python-6b8454bfc272

### Med Priority:
- Modify colors of pie chart to be more distinctive.
- Python server should be two servers! So they can run independently.
- Re-label pie chart.
- Python server should restart upon code change.
- async nature of 'get_estimate' in app.js causes comments to not return to frontend in order (should just call for multiple comments @ once, then return answers for all in one go).
- Refactor comment extraction - just get all comments from mongo, check if contains 'category' after.

### Low priority:
- In react select for user classification, user should have a null option.
- nlp.py feature extractor should have a more useful error if a comment does not have a specific key.
- Instead of adding db=db kwarg to mongo_handler, just patch the var in unittests.
  - Also make the test db the default.
- Get rid of column name in 'args' (server arguments).
- Reinforce (on client and server) that data is JSON format
- style.css is being duplicated (incl. @ index.jsx, also copies w/ webpack.config)
- Move to PostgreSQL
- consider splitting the website and scraper
    a) Redis to communicate
    b) Postgres event notification
    c) Server-sent events: https://www.html5rocks.com/en/tutorials/eventsource/basics/#toc-js-api

