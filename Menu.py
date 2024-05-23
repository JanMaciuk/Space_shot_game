import customtkinter as CTK
import re, os, json, subprocess, sys
from tkinter import Tk, Scrollbar, Text, font, Listbox, Toplevel, Frame
from tkinter.filedialog import askopenfilename

WINDOW_RESOLUTION = "350x440"
WINDOW_TITLE = "Main menu"
DEFAULTS_PATH = "default.json"
FONT_BUTTON = ("Arial", 22)
FONT_LABEL = ("Arial", 14)
WIDTH_BUTTON = int(WINDOW_RESOLUTION.split("x")[0])
CTK.set_appearance_mode("dark")  # Modes: system (default), light, dark
CTK.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

class PromptWindow(CTK.CTkToplevel):
    def __init__(self, parent:CTK.CTk, title:str, text:str) -> None:
        super().__init__(parent)
        self.title(title)
        self.frame = CTK.CTkFrame(self)
        self.frame.grid()
        self.label = CTK.CTkLabel(self.frame, text=text)
        self.label.grid()
        self.button = CTK.CTkButton(self.frame, text="OK", command=self.destroy)
        self.button.grid()
        self.after(10, self.lift)   # Dsiplay the notification above main menu.

class MainMenu(CTK.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry(WINDOW_RESOLUTION)
        self.title(WINDOW_TITLE)
        self.frame = CTK.CTkFrame(self)
        self.frame.grid()
        self.initializeLayout()
        self.currentFilePath:str = DEFAULTS_PATH
        # If a file was passed and loading it succeeds, set it as current file.
        # Otherwise ignore the passed string and load defaults.
        if (len(sys.argv) > 1) and self.loadSettings(sys.argv[1]):   
            self.currentFilePath:str = sys.argv[1]
        else:
            self.loadSettings(DEFAULTS_PATH)

    def initializeLayout(self) -> None:
        '''
        Construct the basic window layout
        '''
        #Buttons:
        buttonNewProfile =    CTK.CTkButton(self.frame, text="New profile", command=self.eventNewProfile, font=FONT_BUTTON, width=WIDTH_BUTTON)
        buttonSelectProfile = CTK.CTkButton(self.frame, text="Select profile", command=self.eventSelectProfile, font=FONT_BUTTON, width=WIDTH_BUTTON)
        buttonSaveSettings =  CTK.CTkButton(self.frame, text="Save settings", command=self.eventSaveSettings, font=FONT_BUTTON, width=WIDTH_BUTTON)
        buttonLaunchGame =    CTK.CTkButton(self.frame, text="Launch game", command=self.eventLaunchGame, font=FONT_BUTTON, width=WIDTH_BUTTON)

        buttonNewProfile.grid(    row=0, column=0, columnspan=2 )
        buttonSelectProfile.grid( row=1, column=0, columnspan=2 )
        buttonSaveSettings.grid(  row=2, column=0, columnspan=2 )
        buttonLaunchGame.grid(    row=3, column=0, columnspan=2 )

        #Read only fields:
        labelProfile = CTK.CTkLabel(self.frame, text="Open profile: ", font=FONT_LABEL)
        self.profile = CTK.CTkLabel(self.frame, text= " ")
        labelScore =  CTK.CTkLabel(self.frame, text="Score: ", font=FONT_LABEL)
        self.score =  CTK.CTkLabel(self.frame, text= " ")
        labelHealth = CTK.CTkLabel(self.frame, text="Health: ", font=FONT_LABEL)
        self.health = CTK.CTkLabel(self.frame, text= " ")
        labelAmmo =   CTK.CTkLabel(self.frame, text="Ammo: ", font=FONT_LABEL)
        self.ammo =   CTK.CTkLabel(self.frame, text= " ")

        labelProfile.grid( row=4, column=0 )
        self.profile.grid( row=4, column=1 )
        labelScore.grid(   row=5, column=0 )
        self.score.grid(   row=5, column=1 )
        labelHealth.grid(  row=6, column=0 )
        self.health.grid(  row=6, column=1 )
        labelAmmo.grid(    row=7, column=0 )
        self.ammo.grid(    row=7, column=1 )

        #Editable fields:
        labelEnemySpeed = CTK.CTkLabel(self.frame, text="Enemy maneuverability: ", font=FONT_LABEL)
        self.enemySpeed = CTK.CTkOptionMenu(self.frame, values=["Low", "Medium", "High"], font=FONT_LABEL)
        labelEnemyHP =    CTK.CTkLabel(self.frame, text="Enemy health: ", font=FONT_LABEL)
        self.enemyHP =    CTK.CTkOptionMenu(self.frame, values=["Low", "Medium", "High"], font=FONT_LABEL)
        labelAsteroidHP = CTK.CTkLabel(self.frame, text="Asteroid durability: ", font=FONT_LABEL)
        self.asteroidHP = CTK.CTkOptionMenu(self.frame, values=["Low", "Medium", "High"], font=FONT_LABEL)
        labelEnemies =    CTK.CTkLabel(self.frame, text="Enemy spawn frequency: ", font=FONT_LABEL)
        self.enemies =    CTK.CTkEntry(self.frame, font=FONT_LABEL)
        labelAsteroids =  CTK.CTkLabel(self.frame, text="Asteroid spawn frequency: ", font=FONT_LABEL)
        self.asteroids =  CTK.CTkEntry(self.frame, font=FONT_LABEL)
        labelAmmoCount =  CTK.CTkLabel(self.frame, text="Supply box spawn frequency: ", font=FONT_LABEL)
        self.supplyCount =  CTK.CTkEntry(self.frame, font=FONT_LABEL)

        labelEnemySpeed.grid( row=8, column=0 )
        self.enemySpeed.grid( row=8, column=1 )
        labelEnemyHP.grid(    row=9, column=0 )
        self.enemyHP.grid(    row=9, column=1 )
        labelAsteroidHP.grid( row=10, column=0 )
        self.asteroidHP.grid( row=10, column=1 )
        labelEnemies.grid(    row=11, column=0 )
        self.enemies.grid(    row=11, column=1 )
        labelAsteroids.grid(  row=12, column=0 )
        self.asteroids.grid(  row=12, column=1 )
        labelAmmoCount.grid(  row=13, column=0 )
        self.supplyCount.grid(row=13, column=1 )
        
        exitButton = CTK.CTkButton(self.frame, text="Quit game", command=self.destroy, font=FONT_BUTTON, width=WIDTH_BUTTON)
        exitButton.grid(row=14, column=0, columnspan=2)

    def loadSettings(self, filePath:str) -> bool:
        '''
        Fill the fields with data read from the file, return value indicates success
        '''
        #Try to read data from the file, checks both file path and file content.
        try:
            profileDict = json.load(open(filePath, "r"))
            for key in ["Score", "Health", "Ammo", "EnemySpeed", "EnemyHealth", "AsteroidDurability", "EnemyCount", "AsteroidCount", "SupplyCount"]:
                if key not in profileDict or not isinstance(profileDict[key], int):
                    raise AssertionError()

        except:
            PromptWindow(self, "Profile read error", "Failed to load the profile file, make sure it's a valid profile.")
            return False
        
        #If we got here, the file is a valid profile, set it as current profile.
        self.currentFilePath = filePath
        #Fill fields with read data
        self.profile.configure(text=os.path.basename(filePath)[0:-5])
        self.score.configure(text=str(profileDict["Score"]))
        self.health.configure(text=str(profileDict["Health"]))
        self.ammo.configure(text=str(profileDict["Ammo"]))
        match profileDict["EnemySpeed"]:
            case 1: self.enemySpeed.set("Low")
            case 2: self.enemySpeed.set("Medium")
            case 3: self.enemySpeed.set("High")
        match profileDict["EnemyHealth"]:
            case 1: self.enemyHP.set("Low")
            case 2: self.enemyHP.set("Medium")
            case 3: self.enemyHP.set("High")
        match profileDict["AsteroidDurability"]:
            case 1: self.asteroidHP.set("Low")
            case 2: self.asteroidHP.set("Medium")
            case 3: self.asteroidHP.set("High")
        self.enemies.delete(0, "end")
        self.enemies.insert(0, str(profileDict["EnemyCount"]))
        self.asteroids.delete(0, "end")
        self.asteroids.insert(0, str(profileDict["AsteroidCount"]))
        self.supplyCount.delete(0, "end")
        self.supplyCount.insert(0, str(profileDict["SupplyCount"]))
        return True

    def newProfile(self) -> None:
        '''
        Create a new profile file and fill with defaults
        '''
        #Ask for a profile/file name and create it:
        dialog = CTK.CTkInputDialog(title="New profile", text="Enter the profile name:")
        fileName = dialog.get_input()
        if not fileName: return     # Action was user canceled.
        if not re.match(r'^[a-zA-Z0-9_-]+$', fileName):
            PromptWindow(self, "Invalid name", "The name can only contain letters, numbers, underscores and hyphens.")
            return
        if len(fileName) > 20:
            PromptWindow(self, "Invalid name", "The name can't be longer than 20 characters.")
            return
        #Create the file:
        filePath = os.path.join(os.getcwd(), "Profiles", fileName + ".json")
        if os.path.exists(filePath):
            PromptWindow(self, "Invalid name", "The profile already exists.")
            return
        with open(filePath, "w") as file:
            with open(DEFAULTS_PATH, "r") as defaults:
                file.write(defaults.read()) # Copy the default settings.
        #Load the new file:
        self.loadSettings(filePath)

    def saveSettings(self) -> bool:
        '''
        Validate field's data, return False if a field is invalid.
        If the data is valid return True and save the data to the file.
        '''
        #Validate profile name:
        if self.currentFilePath == DEFAULTS_PATH: # Nothing to save.
            PromptWindow(self, "No profile", "No profile open, create a new profile first, or open an exisitng one.")
            return False  

        #Construct dictionary from fields:
        try:
            dict = {
                "Score": int(self.score.cget("text")),
                "Health": int(self.health.cget("text")),
                "Ammo": int(self.ammo.cget("text")),
                "EnemySpeed": {"Low":1, "Medium":2, "High":3}[self.enemySpeed.get()],
                "EnemyHealth": {"Low":1, "Medium":2, "High":3}[self.enemyHP.get()],
                "AsteroidDurability": {"Low":1, "Medium":2, "High":3}[self.asteroidHP.get()],
                "EnemyCount": int(self.enemies.get()),
                "AsteroidCount": int(self.asteroids.get()),
                "SupplyCount": int(self.supplyCount.get())
            }
        except:
            PromptWindow(self, "Invalid data", "Invalid data entered, check that values of textboxes are integers.")
            return False
        
        #Validate the read data:
        #Check fields where user can't enter his own values, if they are out of bounds, save file was likely tampered with.
        if  ((dict["Score"] < 0) or (dict["Health"] < 0) or (dict["Ammo"] < 0) or
            (dict["EnemySpeed"] not in [1, 2, 3]) or (dict["EnemyHealth"] not in [1, 2, 3]) or (dict["AsteroidDurability"] not in [1, 2, 3])):
            PromptWindow(self, "Invalid data", "Profile data invalid, you might have loaded a corrupted profile, try creating a new one.")
            return False
        
        #Check fields where user can enter his own values:
        if  ((dict["EnemyCount"] < 1) or (dict["AsteroidCount"] < 1) or (dict["SupplyCount"] < 1) or
             (dict["EnemyCount"] > 12) or (dict["AsteroidCount"] > 12) or (dict["SupplyCount"] > 12)):
            PromptWindow(self, "Invalid data", "Spawn frequencies out of range, check that they are between 1 and 12.")
            return False

        #Save data to json file:
        try:
            with open(self.currentFilePath, "w") as file:
                json.dump(dict, file)
        except:
            PromptWindow(self, "Save error", "File save profile, make sure the file is not open in another program or write protected.")
            return False
        return True     

    def launchGame(self) -> None:
        '''
        Save settings and launch the game
        '''
        if self.saveSettings():
            if int(self.health.cget("text") <= 0):
                PromptWindow(self, "Game over", "Player died, game over, create a new profile.")
                return
            #Launch the game with subprocess.
            subprocess.Popen(["python", "GameName.py", self.currentFilePath])
            #Close the menu.
            self.destroy()


    #Button event handlers:
    def eventSelectProfile(self, event=None) -> None:
        self.loadSettings(askopenfilename())
    def eventNewProfile(self, event=None) -> None:
        self.newProfile()
    def eventSaveSettings(self, event=None) -> None:
        self.saveSettings()
    def eventLaunchGame(self, event=None) -> None:
        self.launchGame()


app = MainMenu()
app.mainloop()