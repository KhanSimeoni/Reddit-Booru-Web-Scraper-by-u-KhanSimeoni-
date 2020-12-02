import praw
from pushshift_py import PushshiftAPI
import time
import re

#Global variables
SUBREDDITS = ["massivefangs"]
BOORUS = []
IMAGE_LIMIT = 10
IMAGE_SOURCES = ["twitter", "pixiv", "imgur", "booru", "rule34", "tumblr", "pinterest"]

#Connect to reddit with a read only account and connect to pushshift
print("Connecting to Reddit & Pushshift...")
startT = time.time()
reddit = praw.Reddit(client_id="6Gm2kQcpi-S2jA",    
                    client_secret="1DitcX_XxE0xirKwi2s7apP-vP2LyQ",
                    user_agent="Python Reddit-Booru Web redditScraper V0.1 (By /u/KhanSimeoni)")
pushshift = PushshiftAPI(reddit)

#Check if connected
elapsedT = round((time.time() - startT) * 1000, 2)
if reddit.read_only == True:
  print("Connection Successful in " + str(elapsedT) + "ms \n")
else:
  print("Connection Error to reddit \n")

#class for scraping reddit (and pushshift) for posts with source links, as well as getting information about the post such as score and postID. This information can also be sorted into a list for further use.
class redditScraper:
#connect to a subreddit - takes in a single string
  def subConnect(self, subreddit):
    subreddit = reddit.subreddit(subreddit)
    return subreddit

#Find all comments with links in a subreddit - takes in the subreddit (string) and how many comments to output (int)
  def subComLinks(self, subreddit, limit):
    comments = pushshift.search_comments(q='https', subreddit=subreddit)
    self.comIDS = []
    for i in comments:
      self.comIDS.append(i)
      if len(self.comIDS) >= limit:
        break
    comment = []
    for i in range(len(self.comIDS)):
      comment.append(reddit.comment(self.comIDS[i]).body)
    return comment

#filter a list of strings with a link for the links only
  def linkFilter(self, text):
      commentURL = []
      regx = r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"

      for i in range(len(text)):
        commentURL.append(re.findall(regx, text[i]))
      return commentURL

#Find the score of the post comments are attached to
  def comPosts(self, subreddit, limit):
    postIDS = []
    self.subComLinks(subreddit, limit)
    for i in range(len(self.comIDS)):
      postIDS.append(reddit.comment(self.comIDS[i]).link_id)
    return postIDS

#Filter out links that are not from specified adresses, and combine the posts with the propor links in the format [post1, link1, post2, link2, ...]
  def linkClean(self, links, posts):
    #splice the lists together
    cleaned = []
    if len(links) == len(posts):
      for i in range(len(links)):
        cleaned.append(posts[i])
        cleaned.append(links[i])
    else:
      print("Error: uneaqual string lengths for func linkClean")
    #flatten the list
    flatList = []
    for i in cleaned:
      if type(i) is list:
        for p in i:
            flatList.append(p)
      else:
        flatList.append(i)
    cleaned = flatList
    #filter out unwanted links
    for i in range(len(cleaned)):
      if "t3_" in cleaned[i] or any(p in cleaned[i] for p in IMAGE_SOURCES):
        pass
      else:
        cleaned[i] = ""
    cleaned[:] = [x for x in cleaned if x != ""]
    return cleaned
    
  #add score and percent upvoted to the list, staggered in the format [postID1, score1, percent1, link1, postID2, score2, percent2, link2, ...]
  def linkScore(self, subreddit, data):
    finished = []
    previous = ""
    for i in range(len(data)):
      if "t3_" in data[i]:
        previous = data[i]
        finished.append(data[i])
      elif previous != "":
        post = reddit.submission(id=previous.replace("t3_", ""))
        finished.append(post.score)
        finished.append(post.upvote_ratio)
        finished.append(data[i])
    return finished



#run the program

#scrape reddit and aquire a list of information about each post, in the format [postID1, score1, percent1, link1, postID2, score2, percent2, link2, ...] 
scraper = redditScraper()
sub = scraper.subConnect(SUBREDDITS[0])
print(sub, ":")
com = scraper.subComLinks(SUBREDDITS[0], IMAGE_LIMIT)
links = scraper.linkFilter(com)
posts = scraper.comPosts(SUBREDDITS[0], IMAGE_LIMIT)
clean = scraper.linkClean(links, posts)
final = scraper.linkScore(SUBREDDITS[0], clean)
print(final)
