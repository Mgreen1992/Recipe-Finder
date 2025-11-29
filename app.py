# file: app.py
# authors: Raphael, Shamsi, Michelle
# how to run Command Line Program: (py -> python.exe and <filename>)
# type the following in the commmand line: 'py app.py' 
# how to run Flask App: flask run 

import requests
import flask
import pyrebase  # Firebase SDK for Python
import time 
import datetime
from datetime import datetime

# create flask app
app = flask.Flask(__name__)

#THIS IS THE FIRE BASE API- DIFFERENT FROM SPOONACULAR
# Firebase configuration - REPLACE WITH YOUR ACTUAL FIREBASE CONFIG
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyA-xhNilKL5XGhczzT69-TBG5JWFwPE0CI",  # 🔑 Replace with your Firebase API key
    "authDomain": "recipe-finder-199c1.firebaseapp.com",
    "projectId": "recipe-finder-199c1",
    "storageBucket": "recipe-finder-199c1.firebasestorage.app",
    "messagingSenderId": "776884550252",
    "appId": "1:776884550252:web:89ce787b03a5c586dbb649",
    "databaseURL": "https://recipe-finder-199c1-default-rtdb.firebaseio.com",  # Add this line
}

# Initialize Firebase
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()  # For Realtime Database
# OR if using Firestore, you might need to use the firebase_admin SDK instead


#THIS IS SPOONACULAR API-DIFFERENT FROM FIREBASE
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
        button_label=button_label,
    )

@app.route('/recipes')
def view_recipes():
    try:
        # Fetch all recipes from Firebase
        all_recipes = db.child("recipes").get()
        
        recipes_list = []
        if all_recipes.each() is not None:
            for recipe in all_recipes.each():
                recipe_data = recipe.val()
                recipe_data['id'] = recipe.key()  # Add the Firebase key as ID
                recipes_list.append(recipe_data)
        
        return flask.render_template('recipes.html', recipes=recipes_list)
        
    except Exception as e:
        print(f"Error fetching recipes: {e}")
        return flask.render_template('recipes.html', recipes=[], error="Failed to load recipes")

# Optional: Add a route for viewing individual recipe details
@app.route('/recipe/<recipe_id>')
def recipe_detail(recipe_id):
    try:
        recipe = db.child("recipes").child(recipe_id).get()
        if recipe.val():
            recipe_data = recipe.val()
            recipe_data['id'] = recipe_id
            return flask.render_template('recipe_detail.html', recipe=recipe_data)
        else:
            return flask.render_template('recipe_detail.html', error="Recipe not found")
    except Exception as e:
        print(f"Error fetching recipe: {e}")
        return flask.render_template('recipe_detail.html', error="Failed to load recipe")

@app.route('/upload', methods=['GET', 'POST'])
def upload_recipe():
    if flask.request.method == 'POST':
        try:
            # Get form data
            recipe_name = flask.request.form.get('recipe_name', '').strip()
            ingredients = flask.request.form.get('ingredients', '').strip()
            instructions = flask.request.form.get('instructions', '').strip()
            cooking_time = flask.request.form.get('cooking_time', '').strip()
            difficulty = flask.request.form.get('difficulty', 'Medium').strip()
            
            # Validation errors list
            errors = []
            
            # Validate Recipe Name
            if not recipe_name:
                errors.append("Recipe name is required")
            elif len(recipe_name) < 2:
                errors.append("Recipe name must be at least 2 characters long")
            elif len(recipe_name) > 100:
                errors.append("Recipe name cannot exceed 100 characters")
            
            # Validate Ingredients
            if not ingredients:
                errors.append("Ingredients are required")
            else:
                # Split and clean ingredients
                ingredient_list = [ingredient.strip() for ingredient in ingredients.split(',') if ingredient.strip()]
                if len(ingredient_list) == 0:
                    errors.append("Please provide at least one valid ingredient")
                elif len(ingredient_list) > 50:
                    errors.append("Too many ingredients (maximum 50)")
                else:
                    # Validate each ingredient
                    for i, ingredient in enumerate(ingredient_list):
                        if len(ingredient) > 100:
                            errors.append(f"Ingredient #{i+1} is too long (max 100 characters)")
                        if any(char in ingredient for char in ['<', '>', ';', '{', '}']):
                            errors.append(f"Ingredient #{i+1} contains invalid characters")
            
            # Validate Instructions
            if instructions:
                if len(instructions) < 10:
                    errors.append("Instructions should be at least 10 characters long if provided")
                elif len(instructions) > 2000:
                    errors.append("Instructions are too long (maximum 2000 characters)")
                # Check for suspicious content
                suspicious_keywords = ['<script', 'javascript:', 'onload=', 'onerror=']
                if any(keyword in instructions.lower() for keyword in suspicious_keywords):
                    errors.append("Instructions contain potentially unsafe content")
            
            # Validate Cooking Time
            if cooking_time:
                try:
                    cooking_time_int = int(cooking_time)
                    if cooking_time_int <= 0:
                        errors.append("Cooking time must be a positive number")
                    elif cooking_time_int > 1440:  # 24 hours in minutes
                        errors.append("Cooking time cannot exceed 24 hours (1440 minutes)")
                except ValueError:
                    errors.append("Cooking time must be a valid number")
            else:
                cooking_time_int = None
            
            # Validate Difficulty
            valid_difficulties = ['Easy', 'Medium', 'Hard']
            if difficulty not in valid_difficulties:
                errors.append("Please select a valid difficulty level")
            
            # If there are validation errors, return them
            if errors:
                return flask.render_template(
                    'upload.html',
                    error="Please fix the following errors:",
                    errors=errors,
                    recipe_name=recipe_name,
                    ingredients=ingredients,
                    instructions=instructions,
                    cooking_time=cooking_time,
                    difficulty=difficulty,
                    success=False
                )
            
            # Prepare recipe data (all data is now validated)
            recipe_data = {
                'name': recipe_name,
                'ingredients': ingredient_list,
                'instructions': instructions,
                'cooking_time': cooking_time_int,
                'difficulty': difficulty,
                'created_at': time.time(),
                'created_at_readable': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Remove None values
            recipe_data = {k: v for k, v in recipe_data.items() if v is not None}
            
            # Save to Firebase Realtime Database
            db.child("recipes").push(recipe_data)
            
            # Show success notification
            return flask.render_template(
                'upload.html',
                success=True,
                message="Recipe uploaded successfully! 🎉",
                recipe_name=recipe_name
            )
            
        except Exception as e:
            print(f"Error uploading recipe: {e}")
            return flask.render_template(
                'upload.html',
                error=f"An unexpected error occurred: {str(e)}",
                success=False
            )
    
    # GET request - show upload form
    return flask.render_template('upload.html', success=None)


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
            .btn-upload {{
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 600;
                color: white;
                transition: all 0.3s ease;
            }}
            .btn-upload:hover {{
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
                <div class="d-flex justify-content-center gap-3">
                    <a href="/" class="btn btn-custom btn-lg mt-3">
                        <i class="fas fa-search me-2"></i>Search Again
                    </a>
                    <a href="/upload" class="btn btn-upload btn-lg mt-3">
                        <i class="fas fa-upload me-2"></i>Upload Recipe
                    </a>
                </div>
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