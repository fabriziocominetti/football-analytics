# Player Recommender Tool

This application provides a user-friendly interface for exploring player data and identifying potential targets for scouting. It displays key metrics for the selected player and showcases similar players based on the applied filters. The tool enhances the scouting process by leveraging data analytics to identify players with comparable playing styles and performance attributes.

**v1** only includes standard data and collected from a single season, while **v2** includes multiple statistics and metrics accross the successive seasons.

![Player Recommender Tool v2](/player-recommender/v2/figures/streamlit-recommender_tool_v2.gif)

[Open Web App](https://huggingface.co/spaces/fcx1/player-recommender)

### About

The "Player Recommender Tool" is a data-driven application designed to aid in football player scouting, focusing on the top five European leagues. The tool provide insights into player performance and recommend similar players based on various metrics.

The project begins by retrieving football player statistics from the top five European leagues using web scraping techniques from FBRef. The collected data includes standard player statistics, defensive actions, passing metrics, possession statistics, miscellaneous metrics, and goalkeeping statistics. The data is then cleaned and prepared for analysis by handling missing values, renaming columns, and converting data types where necessary.

After data preparation, principal component analysis (PCA) is applied to reduce the dimensionality of the dataset while retaining 95% of the variance. Cosine similarity is then calculated based on the PCA-transformed data to identify similar players for a given target player.

The visualization aspect of the project is implemented using Streamlit, a Python library for building interactive web applications. Users can select a target player and apply filters based on age, nationality, and league. The tool displays detailed information about the selected player, including statistics and a player image. Moreover, it recommends similar players based on the selected filters and displays their relevant details.

Possible add-ons includes market value, preferred foot, height and weight.