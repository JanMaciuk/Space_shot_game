import customtkinter as CTK
from tkinter import Tk, Scrollbar, Text, font, Listbox, Toplevel, Frame
from tkinter.filedialog import askopenfilename

WINDOW_RESOLUTION = "350x350"
WINDOW_TITLE = "Main menu"
DEFAULTS_PATH = "defaults.json"
FONT_BUTTON = ("Arial", 22)
FONT_LABEL = ("Arial", 14)
WIDTH_BUTTON = int(WINDOW_RESOLUTION.split("x")[0])
CTK.set_appearance_mode("dark")  # Modes: system (default), light, dark
CTK.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

class MainMenu(CTK.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry(WINDOW_RESOLUTION)
        self.title(WINDOW_TITLE)
        self.frame = CTK.CTkFrame(self)
        self.frame.grid()
        self.currentFilePath:str = DEFAULTS_PATH
        self.initializeLayout()
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
        labelEnemies =    CTK.CTkLabel(self.frame, text="Enemy spawn frequency: ", font=FONT_LABEL)
        self.enemies =    CTK.CTkEntry(self.frame, font=FONT_LABEL)
        labelAsteroids =  CTK.CTkLabel(self.frame, text="Asteroid spawn frequency: ", font=FONT_LABEL)
        self.asteroids =  CTK.CTkEntry(self.frame, font=FONT_LABEL)
        labelAmmoCount =  CTK.CTkLabel(self.frame, text="Supply box spawn frequency: ", font=FONT_LABEL)
        self.ammoCount =  CTK.CTkEntry(self.frame, font=FONT_LABEL)

        labelEnemySpeed.grid( row=8, column=0 )
        self.enemySpeed.grid( row=8, column=1 )
        labelEnemies.grid(    row=9, column=0 )
        self.enemies.grid(    row=9, column=1 )
        labelAsteroids.grid(  row=10, column=0 )
        self.asteroids.grid(  row=10, column=1 )
        labelAmmoCount.grid(  row=11, column=0 )
        self.ammoCount.grid(  row=11, column=1 )
        
        

    def loadSettings(self, filePath:str) -> bool:
        '''
        Fill the fields with data read from the file, return value indicates success
        '''
        #TODO Try to read data from the file
        self.currentFilePath = filePath

        #Read data from file and fill the fields
        pass

    def newProfile(self) -> None:
        '''
        Create a new profile file and fill with defaults
        '''
        #Ask for a profile/file name and create it
        fileName = "TODO"
        filePath = "Append saves folder path to the file name"

        #Copy the defaults to the new file

        #Load the new file
        self.loadSettings(filePath)

    def saveSettings(self) -> bool:
        '''
        Validate field's data, return False if a field is invalid.
        If the data is valid return True and save the data to the file.
        '''
        #Validate data:
        if self.currentFilePath == DEFAULTS_PATH: # Nothing to save
            #TODO: prompt the user to select a player profile.
            return False  

        #Save data to file (self.currentFilePath):
        pass

    def launchGame(self) -> None:
        '''
        Save settings and launch the game
        '''
        if self.saveSettings():
            #Launch the game
            pass
            #Close the menu


    #Button event handlers:
    def eventSelectProfile(self, event) -> None:
        self.loadSettings(askopenfilename())
    def eventNewProfile(self, event) -> None:
        self.newProfile()
    def eventSaveSettings(self, event) -> None:
        self.saveSettings()
    def eventLaunchGame(self, event) -> None:
        self.launchGame()

    

app = MainMenu()
app.mainloop()