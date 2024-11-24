cmake_minimum_required(VERSION 3.10)

# Define the project name and version
project(RecordAudio VERSION 1.0)

# Set the C++ standard to be used
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find the PortAudio package
include_directories("/opt/homebrew/Cellar/portaudio/19.7.0/include")
link_directories("/opt/homebrew/Cellar/portaudio/19.7.0/lib/")
# find_package(PortAudio REQUIRED)

# Include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/src/inputs  # Include the src/inputs folder where audio.h is located
)

# Add the executable target
add_executable(record_audio main.cpp src/inputs/audio.cpp)

# Link the PortAudio library to the executable
target_link_libraries(record_audio PRIVATE portaudio)
