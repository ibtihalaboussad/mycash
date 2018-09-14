MyCash is a website for college students through which they can keep track of their expenditures and get a sense
of how they spent their money during the past few months.
In order to visit the website, all that is needed is to open the "project" folder and use "flask run".

The welcome page contains a presentation of the website and its features, but most importantly, it allows users to
sign up or log in. If users don't fill out a required signup/login field or resort to a wrong type of input, they get
messages with their error and are prompted to change their input in order to proceed.

After users log in or sign up, they are redirected to the "add an expenditure" page. In there, they can input a
date, category, number of dollars, and details that describe their expenditure. This form also displays error messages
in case an element is missing/its type is erroneous. After submitting the form, users are redirected to the same
page in case they want to input more spendings, and what they have already entered gets stored in our database.

Next to "add an expenditure" on the navigation bar is "history" which, as its name suggests, displays all the
expenditures users have inputted on their MyCash account. On top of the list of spendings is a "select" element,
which provides users with different self-descriptive ways to have their history sorted (all methods are related to
time, category, and/or number of dollars).

The "stats" web page is only a "GET" and not "POST" page, where users can view two charts. The first one is a pie
chart that shows what percentage of the money they have spent went toward each MyCash category. The second one
displays the percentage of users' budget that they used per month for the past 3 months.

On the "preferences" web page, users can change their password, email address (under the condition that the new one
they are trying to use is not taken), and their monthly budget. Each "update" button serves to change one the three
variables, so users can choose to only change one or all at any point.

Finally, Log Out just redirects users to the welcome page where they can log in/sign up again.
