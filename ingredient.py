import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

api_json = {"type" : st.secrets['type'],
"project_id" : st.secrets['project_id'],
"private_key_id" : st.secrets['private_key_id'],
"private_key" : st.secrets['private_key'],
"client_email": st.secrets['client_email'],
"client_id" : st.secrets['client_id'],
"auth_uri" : st.secrets['auth_uri'],
"token_uri" : st.secrets['token_uri'],
"auth_provider_x509_cert_url" : st.secrets['auth_provider_x509_cert_url'],
"client_x509_cert_url" : st.secrets['client_x509_cert_url'],
"universe_domain" : st.secrets['universe_domain']}
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive",'https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_dict(api_json, scope)
gc = gspread.authorize(creds)
spreadsheet_key = st.secrets["spreadsheet_key"]

def write_to_google_sheets(data, sheet_number):
    spreadsheet = gc.open_by_key(spreadsheet_key)
    worksheet = spreadsheet.get_worksheet(sheet_number - 1)
    for x in data:
        worksheet.append_row(x)

def get_availabe_meals():
    worksheet = gc.open_by_key(spreadsheet_key).sheet1
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    meals = df['recipe_name'].unique().tolist()
    return meals

def get_availabe_ingredients():
    worksheet = gc.open_by_key(spreadsheet_key).sheet1
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    all_ingredients = df['ingredient_name'].unique().tolist()
    return all_ingredients

def get_all_meal_data():
    worksheet = gc.open_by_key(spreadsheet_key).sheet1
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def Meal_Choser_Tab():
    meals = get_availabe_meals()

    st.title("Choose Meals for the Week:")
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    selected_meal_data = []

    for day in days_of_week:
        col1, col2 = st.columns(2)
        selected_meal = col1.selectbox(f"What are you eating on {day}?", [" "] + meals, key=f"meal_for_{day}")
        number_of_people = col2.number_input("Number of People eating this meal:", min_value=1, max_value=50, step=1, key=f"number_of_people_for_{day}")
        selected_meal_data.append([day, selected_meal, number_of_people])

    if all(st.session_state[f"meal_for_{day}"] for day in days_of_week):
        if st.button("Submit"):
            all_meal_data_df = get_all_meal_data()
            st.success("Data submitted successfully!")
            out_df = pd.DataFrame()

            for x in selected_meal_data:
                day = x[0]
                selected_meal = x[1]
                number_of_people = x[2]

                filtered_df = all_meal_data_df.loc[(all_meal_data_df['recipe_name'] == selected_meal)]
                filtered_df['quantity'] = pd.to_numeric(filtered_df['quantity'], errors='coerce')
                filtered_df['serves_persons'] = pd.to_numeric(filtered_df['serves_persons'], errors='coerce')
                serving_sizes = int(filtered_df['serves_persons'].unique())

                multiply = number_of_people / serving_sizes

                filtered_df['quantity'] = filtered_df['quantity'] * multiply

                out_df = pd.concat([out_df, filtered_df], ignore_index=True)
            result_df = out_df.groupby(['ingredient_name', 'units'])['quantity'].sum()#.reset_index()
            st.write(result_df) 

def Recipe_Builder_Tab():
    def ingredients_page():
        all_ingredients = get_availabe_ingredients()
        st.title("Recipe Ingredients Input")
        recipe_name = st.text_input("Recipe Name:")
        num_ingredients = st.number_input("Number of Ingredients:", min_value=1, max_value=50, step=1)
        serves_persons = st.number_input("Number of People Recipe Serves:", min_value=1, max_value=50, step=1)

        data = []

        for i in range(num_ingredients):
            col1, col2, col3 = st.columns(3)
            ingredient_name = col1.text_input(f"Name of Ingredient {i + 1}", key=f"ingredient_name_new_{i}")
            ingredient_name = col1.selectbox(f"Name of Ingredient {i + 1}", all_ingredients, key=f"ingredient_name_{i}")
            quantity = col2.number_input(f"Quantity {i + 1}", min_value=0, step=10, key=f"quantity_{i}")
            units = col3.selectbox(f"Units {i + 1}", ["g", "unit", "ml", "l", "tsp", "tbsp", "cups"], key=f"units_{i}")
            data.append([recipe_name, serves_persons, ingredient_name, quantity, units])
        
        if all(st.session_state[f"ingredient_name_{i}"] and st.session_state[f"quantity_{i}"] and st.session_state[f"units_{i}"] for i in range(num_ingredients)):
            if st.button("Submit"):
                st.success("Data submitted successfully!")
                write_to_google_sheets(data, 1)
    ingredients_page()

def main():
    tab_selection = st.sidebar.radio("Select Tab:", ["Meal Chooser", "Recipe Builder"])

    if tab_selection == "Meal Chooser":
        Meal_Choser_Tab()
    elif tab_selection == "Recipe Builder":
        Recipe_Builder_Tab()

if __name__ == "__main__":
    main()
