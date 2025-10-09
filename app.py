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

# Add the missing results route
@app.route('/results', methods=['POST'])
def results():
    # Get ingredients from form submission
    ingredients_input = flask.request.form.get('ingredients', '')
    ingredients_list = [item.strip() for item in ingredients_input.split(',')]
    
    # Get recipes from API
    recipes = get_recipes_by_ingredients(ingredients_list)
    
    # Build beautiful HTML response with Bootstrap
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recipe Results</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .recipe-card {{
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 25px;
                transition: transform 0.3s ease;
                border: none;
            }}
            .recipe-card:hover {{
                transform: translateY(-5px);
            }}
            .header-section {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .ingredient-badge {{
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                border-radius: 20px;
                padding: 8px 15px;
                margin: 5px;
                display: inline-block;
            }}
            .missing-badge {{
                background: linear-gradient(45deg, #dc3545, #e83e8c);
                color: white;
                border-radius: 20px;
                padding: 8px 15px;
                margin: 5px;
                display: inline-block;
            }}
            .btn-custom {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 600;
                color: white;
                transition: all 0.3s ease;
            }}
            .btn-custom:hover {{
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                color: white;
            }}
            .recipe-title {{
                color: #2c3e50;
                font-weight: 700;
                margin-bottom: 15px;
            }}
            .section-title {{
                color: #34495e;
                font-weight: 600;
                margin: 20px 0 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section text-center">
                <h1 class="display-4 mb-3" style="color: #2c3e50;">
                    <i class="fas fa-utensils me-3"></i>Recipe Results
                </h1>
                <p class="lead text-muted">Found {len(recipes)} recipes for: <strong>{ingredients_input}</strong></p>
                <a href="/" class="btn btn-custom btn-lg mt-3">
                    <i class="fas fa-search me-2"></i>Search Again
                </a>
            </div>
    """
    
    if recipes:
        for recipe in recipes:
            title = recipe["title"]
            used = [i["name"] for i in recipe["usedIngredients"]]
            missed = [i["name"] for i in recipe["missedIngredients"]]
            recipe_id = recipe["id"]
            
            html += f"""
            <div class="recipe-card">
                <div class="card-body p-4">
                    <h3 class="recipe-title">{title}</h3>
                    
                    <div class="mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-check-circle text-success me-2"></i>Used Ingredients
                        </h6>
                        <div class="d-flex flex-wrap">
            """
            
            for ingredient in used:
                html += f'<span class="ingredient-badge"><i class="fas fa-check me-1"></i>{ingredient}</span>'
            
            html += """
                        </div>
                    </div>
            """
            
            if missed:
                html += f"""
                    <div class="mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-times-circle text-danger me-2"></i>Missing Ingredients
                        </h6>
                        <div class="d-flex flex-wrap">
                """
                
                for ingredient in missed:
                    html += f'<span class="missing-badge"><i class="fas fa-times me-1"></i>{ingredient}</span>'
                
                html += """
                        </div>
                    </div>
                """
            
            html += f"""
                    <div class="text-end mt-4">
                        <a href="https://spoonacular.com/recipes/{title.replace(' ', '-')}-{recipe_id}" 
                           target="_blank" 
                           class="btn btn-custom">
                            <i class="fas fa-external-link-alt me-2"></i>View Full Recipe
                        </a>
                    </div>
                </div>
            </div>
            """
    else:
        html += """
            <div class="recipe-card">
                <div class="card-body p-5 text-center">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h3 class="text-muted">No Recipes Found</h3>
                    <p class="text-muted">Try different ingredients or check your spelling.</p>
                </div>
            </div>
        """
    
    html += """
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return html

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