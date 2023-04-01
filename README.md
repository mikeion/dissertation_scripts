# dissertation_scripts

The /scripts folder contains the code for cleaning and preparing the conversations for analysis.


The Messages come in the following format:
```js
{
  "channel": {
    "id": /* (string) The unique identifier of the channel. */,
    "type": /* (string) The type of the channel (e.g., "GuildTextChat" for a text channel). */,
    "categoryId": /* (string) The unique identifier of the category that the channel belongs to. */,
    "category": /* (string) The name of the category that the channel belongs to. */,
    "name": /* (string) The name of the channel. */,
    "topic": /* (string) The topic of the channel (optional). */
  },
  "dateRange": {
    "after": /* (string) The timestamp representing the start date and time of the message range. */,
    "before": /* (string) The timestamp representing the end date and time of the message range (optional). */
  },
  "messages": [
    {
      "id": /* (string) The unique identifier of the message. */,
      "type": /* (string) The type of the message (e.g., "Default" for a normal message, "Reply" for a reply message). */,
      "timestamp": /* (string) The timestamp representing the date and time the message was sent. */,
      "timestampEdited": /* (string) The timestamp representing the date and time the message was last edited (optional). */,
      "callEndedTimestamp": /* (string) The timestamp representing the date and time the call ended (optional). */,
      "isPinned": /* (boolean) A flag indicating whether the message is pinned in the channel. */,
      "content": /* (string) The content of the message. */,
      "author": {
        "id": /* (string) The unique identifier of the message author. */,
        "name": /* (string) The username of the message author. */,
        "discriminator": /* (string) The discriminator of the message author (used to differentiate users with the same username). */,
        "nickname": /* (string) The nickname of the message author in the server (optional). */,
        "color": /* (string) The color code associated with the author's role (optional). */,
        "isBot": /* (boolean) A flag indicating whether the author is a bot. */,
        "avatarUrl": /* (string) The URL of the author's avatar. */
      },
      "attachments": /* (array) An array of attachment objects associated with the message. Each attachment object contains the following properties: */
      [
        {
          "id": /* (string) The unique identifier of the attachment. */,
          "url": /* (string) The URL where the attachment can be accessed. */,
          "fileName": /* (string) The original file name of the attachment. */,
          "fileSizeBytes": /* (integer) The file size of the attachment in bytes. */
        }
      ],
      "embeds": /* (array) An array of embed objects associated with the message (optional). */,
      "stickers": /* (array) An array of sticker objects associated with the message (optional). */,
      "reactions": /* (array) An array of reaction objects associated with the message (optional). */,
      "mentions": /* (array) An array of user objects representing the users mentioned in the message (optional). /,
"reference": / (object) An object representing the message that this message is a reply to (optional). */
}
]
}
```

1. `conversation_disentanglement.py` breaks each channels message into separate dialogues, based on the metadata that shows cut-off of open and close dialog by the bot.
2. `process_conversations_for_labeling.py`  parses cleaned data files to extract conversation records, sorts records by timestamp to maintain chronological order, groups based on sender-receiver pairs to organize the data into meaningful interactions, and writes the processed records to an output file, ensuring that records for each conversation were grouped together.
3. `clean_and_find_avg.py` - this script cleans the JSON files of the HTML tags that are necessary for Label Studio to read in the files, computes the number of tokens in each dialogue, and then takes an average over any folder (and subsequent subfolder) of JSON files
4. `filter_derivative_bytoken.py` - this script is a token-based filter system to find conversations where students talk about derivative problems. a simple system to start finding relevant conversations to label.
5. `filter_derivative_gpt4.py` - ## This script is used to filter the JSON files that contain the dialogues from the channels. It uses the GPT-4 API to determine whether or not the problem being discussed in the dialogue involves the concept of  the derivative from the Calculus 1 course. It prompts with the following
   > The input is going to a dialogue that took place online in a discord channel devoted to helping students with their math problems.
        Determine whether or not the problem involves the concept of the derivative from the Calculus 1 course. Additionally, looking at the dialogue between the users, determine the contexts (i.e., representations) in which the derivative is being used: That is, (1) graphically, as a slope of a tangent line; (2) verbally, as rate of change; 
        (3) physically, as a velocity in kinematic situations; (4) symbolically, as the limit of the difference quotient, or (5) "using rules to take the derivative"(e.g., a context not listed here). Similarly,
        if the value of derivative is 1, determine whether the problem is being solved with actions that treat the derivative as a ratio (for example, calculating the derivative as the slope of a 
        secant line between two points on a graph), as a limit (for example, calculating the derivative as the limit of the difference quotient), as a function (for example, calculating the slope of the tangent line to the curve
        of the original function at any point on the domain of the function). For the statement of the problem being solved that you will fill in below, try to extract the problem statement from the dialogue.
        Your answer will be in the following format: 
        1. 'derivative:[0 or 1], 
        2. problem:[statement of the problem being solved], 
        3. operator:[ratio, limit, function] 
        4. representational context [0 (if not about the derivative) 1 or 2 or 3 or 4 or 5; given by the representations above if derivative is 1], 
        5. representing topic of the problem:[derivative or other topic], 
        6. explanation:[Rest of explanation]'.
        The rest of the explanation should provide a justification for your answer, for each of the three questions, and provide examples of the operations or actions that the users are using when trying to solve the problem. 
        
         """