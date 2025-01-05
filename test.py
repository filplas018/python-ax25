import pythonax25
import time
import wiringpi as wp

# Inicializace CC1101 pomocí WiringPi
def init_cc1101():
    # Nastavení SPI
    wp.wiringPiSetup()                 # Inicializace WiringPi
    wp.wiringPiSPISetup(0, 500000)     # SPI kanál 0, rychlost 500 kHz

    # Inicializace CS pinu (Chip Select)
    CS_PIN = 25  # BCM GPIO 25
    wp.pinMode(CS_PIN, 1)  # Nastavení jako výstup
    wp.digitalWrite(CS_PIN, 1)  # Deaktivace CS

    return CS_PIN

# Funkce pro odeslání dat přes CC1101
def send_packet_cc1101(cs_pin, data):
    wp.digitalWrite(cs_pin, 0)  # Aktivace CS
    wp.wiringPiSPIDataRW(0, bytes(data))  # Zápis dat přes SPI
    wp.digitalWrite(cs_pin, 1)  # Deaktivace CS

# Hlavní program
def main():
    # Inicializace AX.25
    if pythonax25.config_load_ports() > 0:
        axport = pythonax25.config_get_first_port()
        axdevice = pythonax25.config_get_device(axport)
        axaddress = pythonax25.config_get_address(axport)
        print(f"Port: {axport}, Device: {axdevice}, Address: {axaddress}")
    else:
        print("Žádný AX.25 port nenalezen!")
        exit(1)

    # Inicializace CC1101
    cs_pin = init_cc1101()

    # Vytvoření socketu
    socket = pythonax25.datagram_socket()
    pythonax25.datagram_bind(socket, "N0CALL-1", axaddress)

    # Odeslání zpráv
    dest = "APRS"
    digi = "WIDE1-1"
    messages = [
        "!5000.00N/01000.00E-Test AX.25 přes CC1101!",
        "T#001,045,045,045,045,000,11111111",
        "_08001549c040s060g065t080r001h55b10020"
    ]

    for msg in messages:
        # AX.25 packet encoding
        res = pythonax25.datagram_tx_digi(socket, dest, digi, msg)
        if res < 0:
            print("Chyba při sestavení AX.25 paketu!")
            continue

        # Odeslání přes CC1101
        packet = msg.encode('utf-8')  # Převedení zprávy na bytes
        send_packet_cc1101(cs_pin, packet)
        print(f"Odesláno: {msg}")
        time.sleep(1)

    # Zavření socketu
    pythonax25.close_socket(socket)

if __name__ == '__main__':
    main()
