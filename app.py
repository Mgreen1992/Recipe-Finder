#  file: recipiefinder.py
#  authors: Raphael, Shamsi, Michelle
#  how to run Command Line Program: (py -> python.exe and <filename>)
#  type the following in the commmand line: 'py recipefinder.py' 
#  how to run Flask App: flask run 

import requests
# use 'pip install flask'in your command line
import flask

# create flask app
app = flask.Flask(__name__)


API_KEY = "869383fda5b5465087a630f231271e3e"  # 🔑 Replace this with your actual Spoonacular API key
BASE_URL = "https://api.spoonacular.com/recipes/findByIngredients"

def get_recipes_by_ingredients(ingredients, number=5):
    # Prepare query parameters
    params = {
        "ingredients": ",".join(ingredients),
        "number": number,
        "ranking": 1,  # 1 = maximize used ingredients
        "ignorePantry": True,
        "apiKey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return []

    return response.json()

# Webapp version
@app.route('/')
def home():
    # Create variables to pass to the HTML page
    title = "Recipe Finder"
    prompt = "Enter the ingredients you have (comma-separated):"
    instructions = "Type the ingredients below and press 'Find Recipes' to get suggestions!"
    button_label = "Find Recipes"

    # Render the HTML page with variables
    return flask.render_template(
        'index.html',
        title=title,
        prompt=prompt,
        instructions=instructions,
        button_label=button_label
    )

if __name__ == '__main__':
    app.run(debug=True) # debug=True enables debug mode for development

# Command line version
# Step 4: User input
# user_input = input("Enter the ingredients you have (comma-separated): ")
# user_ingredients = [item.strip().lower() for item in user_input.split(',')]

# # Step 5: Fetch and display recipes
# recipes = get_recipes_by_ingredients(user_ingredients)

# if recipes:
#     print("\n🍽️ Recipes you can make:")
#     for recipe in recipes:
#         title = recipe["title"]
#         used = [i["name"] for i in recipe["usedIngredients"]]
#         missed = [i["name"] for i in recipe["missedIngredients"]]
#         print(f"\n🔹 {title}")
#         print(f"   ✅ Used ingredients: {', '.join(used)}")
#         if missed:
#             print(f"   ❌ Missing ingredients: {', '.join(missed)}")
#         print(f"   📎 Recipe link: https://spoonacular.com/recipes/{title.replace(' ', '-')}-{recipe['id']}")
# else:
#     print("\n❌ No recipes found. Try different or more ingredients.")
