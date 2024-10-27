# EV3connect: A simple Project to control an EV3 robot via Bluetooth

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Usage](#usage)
- [Installation](#installation)
- [Error Handling and Pairing](#error-handling-and-pairing)

## Introduction

###### EV3connect is a simple project that enables control of an EV3 robot via Bluetooth. It provides a straightforward way to communicate with the EV3 robot, using a graphical user interface (GUI).

## Features

- Bluetooth connectivity: Establishes a connection with the EV3 robot via Bluetooth.
- Command sending: Sends commands to the EV3 robot to control its movements and actions.
- Data reception: Receives data from the EV3 robot, such as sensor readings and motor status.
- Simple GUI: Provides a simple and intuitive GUI for interacting with the EV3 robot.
## Usage

### Connecting to the EV3 Robot

###### To connect to the EV3 robot, follow these steps:

#### Step 1: Turn on the EV3 robot and enable Bluetooth mode

>**Note:** Ensure the EV3 robot is turned on and in Bluetooth mode.

#### Step 2: Run the EV3connect script as python or compiled executable

>**Note:** In order to run the executable just run it like a normal application.

```bash
python main.py
```
#### Step 3: Pair with the EV3 robot

* Choose the name of the EV3 robot you want to connect to from the list of found devices in the UI.
* Accept the connection and set a password on the EV3 robot.
* Click on the toast notification that appears on your Windows PC and enter the password you set on the EV3 brick.

## Installation

There are two ways to install EV3connect:

### Option 1: Download the Compiled Standalone Executable

1. Go to the [releases tab](https://github.com/PauWol/EV3connect/releases) of the EV3connect repository.
2. Download the compiled standalone executable for your operating system.
3. Run the EV3connect executable.

### Option 2: Install from Source

1. Clone or download the EV3connect repository:
	* Using Git: ``git clone https://github.com/PauWol/EV3connect.git``
	* Or download directly from GitHub: [Download](https://github.com/PauWol/EV3connect/archive/refs/heads/main.zip) and extract the contents.
2. Install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```
3. Run the EV3connect script using the following command:

```bash
python main.py
```

## Error Handling and Pairing

### Connection Issues

If you encounter issues connecting to the EV3 brick, try the following:

* If you previously ran the application and then closed it, try turning off and then on the Bluetooth on your PC. This will reset the connection and allow you to try again.

### Pairing Issues

When pairing the EV3 brick with your PC, make sure to:

* Keep an eye on the EV3 brick's screen, as you will be prompted to accept the connection and set a password.
* Click on the toast notification that appears on your Windows PC and enter the password you set on the EV3 brick.

### General Error Handling

If an error occurs, try the following:

* Close the EV3connect application.
* Restart the Bluetooth on both your PC and the EV3 brick.
* Try running the EV3connect application again.

>**Note** Some errors may occur during the usage of the application.Keep in mind that the application is not actively maintained.And there is no guarantee that it will work as expected.