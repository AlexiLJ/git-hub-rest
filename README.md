# **This app uses FastAPI app to get 2 endpoints, in order to:**

##  1.   http://127.0.0.1:8000/github-events/7 (where last digit is offset)

     - Calculate the average time between pull requests for a given repository.

     - Return the total number of events grouped by the event type for a given
       offset. The offset determines how much time we want to look back i.e., an
       offset of 10 means we count only the events which have been created in the
       last 10 minutes.


## 2.    http://127.0.0.1:8000/github-events-plot/20 (where last digit is offset)

     -Add another REST API endpoint providing a meaningful visualization of one of  existing metrics or a newly introduced metric.


# **How to run app:**

    1. create github token and add it to sys. variables as 'GIT_HUB_TOCKEN', 
       or detelete in the row 14 os.environ part and add token string instead.
    2. run pip install -r requirements.txt
    3. run main.py and acces endpoints in browser : 
                                                    http://127.0.0.1:8000/github-events/7 
                                                    http://127.0.0.1:8000/github-events-plot/20
    choose offset as needed.