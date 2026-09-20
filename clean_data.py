import pandas as pd
import mysql.connector as mysql

def clean_data(df):
    print("Cleaning data\n")
    var = df.drop(columns=["super_over", "method"])
    var = var.dropna(subset=["season", "team1", "team2"])
    def fix_season(x):
        x = str(x)
        if "/" in x:
            return int(x.split("/")[1]) + 2000
        else:
            return int(x)
    var["season"] = var["season"].apply(fix_season)
    var["date"] = pd.to_datetime(var["date"], format="%d-%m-%Y", errors="coerce")
    var = var.dropna(subset=["date"])
    print("Data cleaned successfully\n")
    save_cleaned_data(var)
    return var
def save_cleaned_data(var):
    print("Saving cleaned data\n")
    var.to_csv("cleaned_matches.csv", index=False)
    print("Data saved\n")
try:
    df = pd.read_csv("C:\\Users\\KIIT\\OneDrive\\Documents\\matches.csv")
    if df.empty:
        print("DataFrame is empty\n")
    else:
        print("Data loaded successfully\n")
        var = clean_data(df)
except FileNotFoundError:
    print("File not found. Please check the file path.\n")
try:
    connection = mysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="ipl_db"
    )
    if connection.is_connected():
        print("Successfully connected to MySQL!")
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cleaned_matches(
            id INT,
            season INT,
            city VARCHAR(100),
            date DATE,
            match_type VARCHAR(50),
            player_of_match VARCHAR(100),
            venue VARCHAR(100),
            team1 VARCHAR(100),
            team2 VARCHAR(100),
            toss_winner VARCHAR(100),
            toss_decision VARCHAR(50),
            winner VARCHAR(100),
            result VARCHAR(50),
            result_margin VARCHAR(50),
            target_runs INT,
            target_overs INT,
            umpire1 VARCHAR(100),
            umpire2 VARCHAR(100)
        )
        """
        cursor.execute(create_table_query)
        cursor.execute("TRUNCATE TABLE cleaned_matches")
        query = """
        INSERT INTO cleaned_matches (
            id, season, city, date, match_type, player_of_match, venue,
            team1, team2, toss_winner, toss_decision, winner,
            result, result_margin, target_runs, target_overs,
            umpire1, umpire2
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for i in range(len(var)):
            row = var.iloc[i].tolist()
            clean_row = []
            for val in row:
                if pd.isna(val):
                    clean_row.append(None)
                elif isinstance(val, pd.Timestamp):
                    clean_row.append(val.strftime('%Y-%m-%d'))
                elif hasattr(val, "item"):
                    clean_row.append(val.item())
                else:
                    clean_row.append(val)
            cursor.execute(query, tuple(clean_row))
        connection.commit()
        cursor.close()
        print("Data inserted successfully into database\n")
except mysql.Error as e:
    print("Error:", e)