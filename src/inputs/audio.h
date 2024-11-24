#ifndef AUDIO_H
#define AUDIO_H

#include <portaudio.h>
#include <stdio.h>

char getKeyPress();

// Callback function for audio recording
int recordCallback(const void *inputBuffer, void *outputBuffer,
                   unsigned long framesPerBuffer,
                   const PaStreamCallbackTimeInfo *timeInfo,
                   PaStreamCallbackFlags statusFlags,
                   void *userData);

// Main function to start the audio recording process
void startAudioRecording();

#endif