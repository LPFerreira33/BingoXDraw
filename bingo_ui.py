import random
import pygame
import PySimpleGUI as sg
import azure.cognitiveservices.speech as speechsdk

from bingo_utils import save_numbers_to_file, load_numbers_from_file, withdraw_number, cancel_withdraw, add_number
from bingo_utils import check_bingo, initialize_speech_service

if __name__ == "__main__":
    # Initialize speech service for additional voice features 
    # Note: If no information about about Azure Speech Voices, program will run without voices
    speech_config, audio_config, voice_languages = initialize_speech_service(dotenv_path="user_files/secrets.env")

    # Set the theme for the GUI
    sg.theme("DarkGrey1")

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load sound files
    withdraw_sounds = [pygame.mixer.Sound("sounds/withdraw.mp3"), pygame.mixer.Sound("sounds/withdraw_2.mp3")]
    cancel_sound = pygame.mixer.Sound("sounds/cancel_withdraw.mp3")
    win_sound = pygame.mixer.Sound("sounds/bingo_win.wav")
    loss_sound = pygame.mixer.Sound("sounds/bingo_loss.mp3")

    # Set lower volume to withdraw_sounds
    for sound in withdraw_sounds:
        sound.set_volume(0.1)

    # Default max bingo number
    max_bingo_number = 0

    # Initialize bingo_numbers and withdrawn_numbers
    bingo_numbers, withdrawn_numbers = load_numbers_from_file("user_files/bingo_data.pkl", max_bingo_number)

    # Define the layout of the GUI
    layout = [
        [sg.Text("BingoXDraw", font=("Helvetica", 20), justification='center')],
        [sg.Text("Let's play some bingo!", font=("Helvetica", 14))],
        [sg.Text("Choose Voice Language:", font=("Helvetica", 12)),
            sg.Combo(list(voice_languages.keys()), default_value="Português (Portugal)", key="-VoiceLanguage-", readonly=True)],
        [sg.Text("Enter Max Bingo Number: ", font=("Helvetica", 12)), 
            sg.InputText(default_text=str(max_bingo_number), key="-MaxBingoNumber-", size=(10, 1)), 
            sg.Button("Create Bingo Numbers", size=(20, 1))],
        [sg.Text("Bingo Numbers: ", font=("Helvetica", 12))],
        [sg.Multiline(", ".join(map(str, bingo_numbers)), size=(60, 4), key="-BingoNumbers-", disabled=True, 
                        autoscroll=True, expand_x=True, expand_y=True, font=('Helvetica', 12))],
        [sg.Text("Withdrawn Bingo Numbers: ", font=("Helvetica", 12))],
        [sg.Multiline(", ".join(map(str, withdrawn_numbers)), size=(60, 4), key="-WithdrawnNumbers-", disabled=True,
        autoscroll=True, expand_x=True, expand_y=True, font=('Helvetica', 12))],
        [sg.Button("Withdraw Number", size=(15, 2), button_color=('white', 'green')),
            sg.Button("Cancel Last Withdraw", size=(20, 2), button_color=('white', 'red'))],
        [sg.Text("Have a new Bingo number? Add it!", font=("Helvetica", 12))],
        [sg.InputText(key="-AddNumber-", size=(10, 1)), sg.Button("Add Number", size=(15, 1))],
        [sg.Text("Check if numbers are withdrawn:", font=("Helvetica", 12))],
        [sg.InputText(key="-NumbersToCheck-", size=(20, 1)), sg.Button("Check Numbers", size=(15, 1))],
        [sg.Button("Exit", size=(10, 2), button_color=('white', 'grey'))],
    ]

    # Create the window with resizable option
    window = sg.Window("BingoXDraw", layout, resizable=True, finalize=True, size=(800, 600), icon="user_files/bingo_icon.ico")

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            # Save current state before closing the window
            save_numbers_to_file("user_files/bingo_data.pkl", bingo_numbers, withdrawn_numbers)
            break
        elif event == "Withdraw Number":
            # Play a random withdrawn sound
            random.choice(withdraw_sounds).play()

            # Retrieve the selected language information
            language_info = voice_languages[values["-VoiceLanguage-"]]
            withdraw_text = language_info["text"]
            speech_config.speech_synthesis_voice_name = language_info['voice']

            # Withdraw a number from the available bingo numbers and add it to the withdrawn list
            withdrawn_number = withdraw_number(bingo_numbers, withdrawn_numbers)

            # Generate the speech text for the withdrawn number
            withdrawn_number_text = f"{withdraw_text} {withdrawn_number}!"

            # Use the speech synthesizer to read the generated text aloud
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            speech_synthesizer.speak_text_async(withdrawn_number_text).get()

            if withdrawn_number is not None:
                # Update GUI display after withdrawal
                window["-BingoNumbers-"].update(", ".join(map(str, bingo_numbers)))
                window["-WithdrawnNumbers-"].update(", ".join(map(str, withdrawn_numbers)))
                # Display a popup message for the withdrawn number
                sg.popup(f"Withdrew number: {withdrawn_number}")
            else:
                sg.popup("No more numbers left to withdraw!")
        elif event == "Cancel Last Withdraw":
            if withdrawn_numbers:
                # Confirm before canceling the last withdrawal
                confirm_cancel = sg.popup_yes_no("This will cancel the last withdrawal. Do you want to proceed?",
                                                title="Warning")
                if confirm_cancel == "Yes":
                    # Play the cancel sound
                    cancel_sound.play()

                    # Cancel the last withdrawal and update GUI display
                    canceled_number = cancel_withdraw(bingo_numbers, withdrawn_numbers)
                    window["-BingoNumbers-"].update(", ".join(map(str, bingo_numbers)))
                    window["-WithdrawnNumbers-"].update(", ".join(map(str, withdrawn_numbers)))
                    sg.popup(f"Canceled withdrawal of number: {canceled_number}")
            else:
                sg.popup("No withdrawal to cancel!")
        elif event == "Add Number":
            try:
                # Convert input to an integer and add to bingo numbers
                number_to_add = int(values["-AddNumber-"])
                add_number(bingo_numbers, number_to_add)
                # Update GUI display after adding a number
                window["-BingoNumbers-"].update(", ".join(map(str, bingo_numbers)))
                window["-WithdrawnNumbers-"].update(", ".join(map(str, withdrawn_numbers)))
                # Display a popup message for the added number
                sg.popup(f"Added number: {number_to_add}")
            except ValueError:
                sg.popup("Invalid input. Please enter a valid number.")
        elif event == "Create Bingo Numbers":
            # Confirm before overriding bingo numbers
            confirm = sg.popup_yes_no("This will override the bingo numbers. Do you want to proceed?",
                                    title="Warning")
            if confirm == "Yes":
                try:
                    # Convert input to an integer and create new bingo numbers
                    max_bingo_number = int(values["-MaxBingoNumber-"])
                    bingo_numbers = list(range(1, max_bingo_number + 1))
                    withdrawn_numbers = []  # Reset withdrawn numbers
                    # Update GUI display after creating new bingo numbers
                    window["-BingoNumbers-"].update(", ".join(map(str, bingo_numbers)))
                    window["-WithdrawnNumbers-"].update("")
                    # Save the new state to the file
                    save_numbers_to_file("user_files/bingo_data.pkl", bingo_numbers, withdrawn_numbers)
                except ValueError:
                    sg.popup("Invalid input. Please enter a valid number for Max Bingo Number.")
        elif event == "Check Numbers":
            try:
                # Convert input to a list of integers and check bingo status
                numbers_to_check = list(map(int, values["-NumbersToCheck-"].split(',')))
                results, is_bingo = check_bingo(numbers_to_check, withdrawn_numbers)
                # Play win or loss sound accordingly
                win_sound.play() if is_bingo else loss_sound.play()
                # Prepare result text for display in a popup
                result_text = "\n".join(f"{num}: {res}" for num, res in zip(numbers_to_check, results))
                result_text += "\nBINGO!!!!!!!!!!!!" if is_bingo else "\nNot bingo :("
                # Display a popup message with the results
                sg.popup(result_text)
            except ValueError:
                sg.popup("Invalid input. Please enter a valid list of numbers.")

    # Close the window
    window.close()