In order to implement MyCash, I used Python, SQL, Javascript, HTML, and CSS.

Regarding the frontend, I resorted to bootstrap in order to make the design of my website mobile friendly and
user friendly. I used navigation bars that can collapse, columns and containers whose width changes depending on
the screen's size, and forms that use adaptive design to adjust to the device.I used button hovers, smooth scrolling,
and a unified theme color to provide users with a pleasant experience interacting with the website.

I also used javascript window.alerts a lot instead of redirecting users to new templates, in order to reduce the
number of times they would have to wait for new pages to get loaded and start all over again (when they input wrong
information, for instance).

I tried to link application.py data to almost every template through jinja, in order to be responsive to users' input
since MyCash is made of several forms. One of the parts that gave me the most trouble was connecting my SQL database
to users' input or to what I would output (like charts and history); I ended up often using SQL SELECT statements
to link tables to python, then passed those lists to script elements and tried to adapt them to javascript usage as
arrays.

In order to design the "/stats" page, I used Google API for pie charts and HighCharts for bar ones. Because the data
I wanted to include in the graphs solely depended on SQL tables, I resorted to the aforementioned transformation
of python lists into javascript arrays/lists of arrays that could be used by the API (using 'safe' when copying
a python list into a javascript array for example to ensure the latter could be safely used).

In the same context, I also opted for setting values for "select" items' options so that I could connect the user's
preferences (in terms of sorting methods, for example) to what I was presenting on their screen.

Overall, the experience of making a data-focused responsive website was very rewarding. I was finally able to get
a sense, however small, of data science's usage to develop interactive software, and this time with no distribution code,
which allowed me build a website from scratch and learn a lot from the issues/constraints.