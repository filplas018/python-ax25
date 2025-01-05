import pythonax25
import time
import RPi.GPIO as GPIO
import spidev

# Initialize CC1101 with RPi.GPIO and SPI
def init_cc1101():
    # Set up the GPIO mode
    GPIO.setmode(GPIO.BCM)
    
    # Set the CS (Chip Select) pin
    CS_PIN = 25  # You can adjust this to your setup if necessary
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.output(CS_PIN, GPIO.HIGH)  # Deselect CC1101 initially

    # Set up SPI communication
    spi = spidev.SpiDev()
    spi.open(0, 0)  # SPI channel 0, CE0 (CE1 if you're using the other SPI port)
    spi.max_speed_hz = 500000  # Set SPI speed to 500 kHz (adjust as needed)
    
    return spi, CS_PIN

# Function to send data through CC1101
def send_packet_cc1101(spi, cs_pin, data):
    GPIO.output(cs_pin, GPIO.LOW)  # Activate the chip (select CC1101)
    spi.xfer2(data)  # Send the data (xfer2 transfers and returns data)
    GPIO.output(cs_pin, GPIO.HIGH)  # Deactivate the chip (deselect CC1101)

# Main program
def main():
    # Load AX.25 configuration
    if pythonax25.config_load_ports() > 0:
        axport = pythonax25.config_get_first_port()
        axdevice = pythonax25.config_get_device(axport)
        axaddress = pythonax25.config_get_address(axport)
        print(f"Port: {axport}, Device: {axdevice}, Address: {axaddress}")
    else:
        print("No AX.25 port found!")
        exit(1)

    # Initialize CC1101
    spi, cs_pin = init_cc1101()

    # Create AX.25 socket
    socket = pythonax25.datagram_socket()
    pythonax25.datagram_bind(socket, "N0CALL-1", axaddress)

    # Messages to send
    dest = "APRS"
    digi = "WIDE1-1"
    messages = [
        "!5000.00N/01000.00E-Test AX.25 from Raspberry Pi!",
        "T#001,045,045,045,045,000,11111111",
        "_08001549c040s060g065t080r001h55b10020"
    ]

    for msg in messages:
        # Encode the AX.25 packet
        res = pythonax25.datagram_tx_digi(socket, dest, digi, msg)
        if res < 0:
            print("Error encoding AX.25 packet!")
            continue

        # Send the packet using CC1101
        packet = list(msg.encode('utf-8'))  # Convert the message to a byte list
        send_packet_cc1101(spi, cs_pin, packet)
        print(f"Sent: {msg}")
        time.sleep(1)  # Delay between packets

    # Close the socket
    pythonax25.close_socket(socket)
    spi.close()

if __name__ == '__main__':
    main()
