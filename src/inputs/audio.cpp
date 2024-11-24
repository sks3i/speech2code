#include "audio.h"
#include <iostream>
#include <unistd.h>
#include <termios.h>

#define SAMPLE_RATE 44100
#define FRAMES_PER_BUFFER 256
#define NUM_CHANNELS 1
#define DITHER_FLAG 0
#define SAMPLE_FORMAT paInt16
#define PRINTF_DEBUG 0

// Function to get a keypress without blocking (cross-platform for Linux/macOS)
char getKeyPress() {
    struct termios oldt, newt;
    char ch;
    
    tcgetattr(STDIN_FILENO, &oldt);    // Get the terminal settings
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);  // Disable canonical mode and echoing
    tcsetattr(STDIN_FILENO, TCSANOW, &newt); // Apply the new settings
    ch = getchar();    // Get the character
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);  // Restore the old terminal settings
    return ch;
}

int recordCallback(const void *inputBuffer, void *outputBuffer,
                   unsigned long framesPerBuffer,
                   const PaStreamCallbackTimeInfo *timeInfo,
                   PaStreamCallbackFlags statusFlags,
                   void *userData) {
    FILE *outputFile = (FILE *)userData;
    fwrite(inputBuffer, sizeof(short), framesPerBuffer, outputFile);
    return paContinue;
}

void startAudioRecording() {
    PaError err;
    FILE *outputFile;
    PaStream *stream;
    bool isRecording = false;

    // Initialize PortAudio
    err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
        return;
    }

    // Open the output file to save audio
    outputFile = fopen("audio_output.raw", "wb");
    if (outputFile == NULL) {
        std::cerr << "Could not open file for writing." << std::endl;
        return;
    }

    // Open the audio stream
    err = Pa_OpenDefaultStream(&stream, NUM_CHANNELS, 0, SAMPLE_FORMAT, SAMPLE_RATE,
                               FRAMES_PER_BUFFER, recordCallback, outputFile);
    if (err != paNoError) {
        std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
        return;
    }

    // Start the audio stream
    err = Pa_StartStream(stream);
    if (err != paNoError) {
        std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
        return;
    }

    std::cout << "Press and hold the spacebar to start recording, release to stop..." << std::endl;

    // Monitor the spacebar for press and release
    while (true) {
        char ch = getKeyPress();  // Get keypress without blocking
        
        if (ch == ' ' && !isRecording) {
            // Start recording when spacebar is pressed
            std::cout << "Recording..." << std::endl;
            isRecording = true;
        }
        
        if (ch != ' ' && isRecording) {
            // Stop recording when spacebar is released
            std::cout << "Recording stopped." << std::endl;
            break;
        }
        
        // Continue recording if the spacebar is pressed
        if (isRecording) {
            // Do nothing, just keep recording
        }
    }

    // Stop the audio stream after the recording ends
    err = Pa_StopStream(stream);
    if (err != paNoError) {
        std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
    }

    err = Pa_CloseStream(stream);
    if (err != paNoError) {
        std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
    }

    // Clean up
    fclose(outputFile);
    Pa_Terminate();

    std::cout << "Recording saved to audio_output.raw" << std::endl;
}