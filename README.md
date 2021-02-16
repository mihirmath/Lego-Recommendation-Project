# CS50 Final Project - Lego Recommender
#### Video Demo:  https://www.youtube.com/watch?v=z5JpmVNULwk
#### Description:
When I first started thinking about my CS50 final project, I knew I wanted to use real data. This was important to me because real data can turn even a small program into a real world application. Instead of brainstorming ideas to begin the thought process, I looked on the website Kaggle for the best dataset I could find. I happened to come across a Lego dataset that had around 7000 legosets and a lot of data for them. Once I decided that I wanted a project based around this dataset, I brainstormed ideas that would apply it.

Brainstorming ideas was pretty difficult as there were so many different options. I knew that I wanted to build a website using flask because that would challenge me to use everything I learned from CS50 on the client side and server side. I decided to make a recommendation system because I realized that many people just buy Legos on the spot and do not consider their preferences or their children’s preferences.

When building my website from the ground up, I ran into quite a few obstacles. The most difficult feature of my project was implementing the favorites system. For this feature, I had to learn about using different classes and look around for certain javascript functions that would help me. I also realized that I had to send data to the server when the favorite button is clicked. I searched around for the best way to implement this and I realized that ajax was the best option. However, I had never used ajax and the syntax was quite new and cryptic for me. I had to take a couple days and learn a lot of ajax syntax. In fact, I made a separate project that just used ajax and python to test out my new skills. I then took the skills I learned from the smaller “test” project and applied them to my final project.

When you first get to my website, you have to register for an account. Once you click register, you will be taken to the main page where you can get recommendations for legosets. The user gets to decide what theme they would like the legoset to be, their budget, and how many pieces they want in the legoset. When you click get recommendations, it will show you all the legosets that are recommended to you based on your parameters. In the table you can see the legosets name, price, and how many pieces it has. If you click on the name, you can see a picture of the legoset when it is complete. You can also favorite any legosets you like by clicking on the star icon. You can view all of your favorites by clicking on the favorites tab. Each user will be able to view all of their favorites accumulated over time. Another feature of this website is that you can view the most popular legosets from our users. To do this click on the popular legosets tab and it will show you the 25 most popular legosets. When you are done, you can log out of the website. 

Here are a list of all the significant files in my project as well as a descriptions for what functionality they have: 
Files:
index.html - Gives the user a form that prompts them for parameters for their recommendation
login.html - Where the user logs in
populars.html - Prints the 25 most popular legosets
recommendation.html - Prints the legosets recommended to the user
register.html - Where the user registers
application.py - Server side of the website
legosets.db - Database with users, user favorites, and legosets
