import sys
import tkinter as tk
import requests
from ttkHyperlinkLabel import HyperlinkLabel
import myNotebook as nb
from config import config
import json
from typing import Optional
from theme import theme
from classes import Cargo
import threading


this = sys.modules[__name__]  # holding globals

this.statusFrame = Optional[tk.Frame]
this.statusLabel = Optional[tk.Label]
this.tipLabel = Optional[tk.Label]
this.unsentDeliveries = []
this.cargo = Cargo()
this.autoSendVar = tk.IntVar()
this.dirStr = ""
this.currentMarket = {}
this.currentStation = {}

def sendData():
    this.send.config(state = tk.DISABLED)
    deliveries = this.unsentDeliveries.copy()
    this.unsentDeliveries = []
    if len(deliveries) == 0:
        if this.autoSendVar.get() == 0:
            this.send.config(state = tk.ACTIVE)
        return
    deliveriesJson = json.dumps({"deliveries": deliveries})
    postResponse = requests.post("https://www.station-builder.free.nf/deliveryif.php", json=deliveriesJson)
    if postResponse.text[-9:-1] == "Accepted":
        print(postResponse.text)
        this.statusLabel.config(text="Deliveries sent!")
        if this.autoSendVar.get() == 0:
            this.send.config(state = tk.ACTIVE)

def sendDataInitiator():
    sendThread = threading.Thread(target=sendData)
    sendThread.start()

def disableButton():
    if this.autoSendVar.get() == 1:
        this.send.config(state = tk.DISABLED)
    elif this.autoSendVar.get() == 0:
        this.send.config(state = tk.ACTIVE)

def plugin_app(parent: tk.Frame) -> tk.Frame:
    this.statusFrame = tk.Frame(parent)
    tk.Label(this.statusFrame, text="Delivery Tracker").grid(column=0, row=0, columnspan=2)
    this.statusLabel = tk.Label(this.statusFrame, text="Deliveries will show up here.")
    this.statusLabel.grid(column=0, row=1, columnspan=2)
    this.autoSend = tk.Checkbutton(this.statusFrame, text="Send automatically", foreground="dark orange", variable=this.autoSendVar, command=disableButton)
    this.autoSend.grid(column=0, row=2)
    this.send = tk.Button(this.statusFrame, text="Send", command=sendDataInitiator)
    this.send.grid(column=1, row=2)
    this.tipLabel = tk.Label(this.statusFrame, text="")
    this.tipLabel.grid(column=0, row=3, columnspan=2)
    return this.statusFrame

def plugin_start3(pluginDir):
    this.dirStr = str(pluginDir)
    commodsFile = open(this.dirStr + "\\items.json", "r").read()
    this.commodities = json.loads(commodsFile)
    return "Delivery Tracker"

def journal_entry(cmdr, is_beta, system, station, entry, state):
    if entry["event"] == "Market": # Market and MarketBuy are workarounds for EDMC sometimes being slow to send/receive data
        this.currentMarket = {"ID": entry["MarketID"], "Station": entry["StationName"],  "System": entry["StarSystem"]}

    elif entry["event"] == "Docked":
        this.currentStation = {"StationName" : entry["StationName"]}

    if entry["event"] == "MarketBuy":
        if this.currentMarket["ID"] == entry["MarketID"]:
            this.cargo.buyCargo({entry["Type"]: entry["Count"]}, this.currentMarket["System"], this.currentMarket["Station"])

    elif entry["event"] == "Cargo":
        prevLen = len(this.unsentDeliveries)
        this.unsentDeliveries.extend(this.cargo.updateCargo(state["Cargo"], system, this.currentStation["StationName"]))
        for x in range(prevLen, len(this.unsentDeliveries)):
            if this.unsentDeliveries[x]["Name"] in this.commodities:
                this.unsentDeliveries[x]["Name"] = this.commodities[this.unsentDeliveries[x]["Name"]]["name"]
            strPrep = "Delivery " + str(x+1) + ":\nOrigin: " + this.unsentDeliveries[x]["OriginSystem"] + ", " + this.unsentDeliveries[x]["OriginStation"]
            strPrep += "\nCommodity: " + this.unsentDeliveries[x]["Name"] + " " + str(this.unsentDeliveries[x]["Count"])
            strPrep += "\nDestination: " + this.unsentDeliveries[x]["DestinationSystem"] + ", " + this.unsentDeliveries[x]["DestinationStation"] + "\n"
            getText = this.statusLabel.cget("text")
            if getText == "Deliveries will show up here." or getText == "Deliveries sent!":
                this.statusLabel.config(text=strPrep)
            else:
                this.statusLabel.config(text=getText + strPrep)

    elif entry["event"] == "StartJump":
        this.currentStation = {}
        if this.autoSendVar.get() == 1:
            sendThread = threading.Thread(target=sendData)
            sendThread.start()

    elif entry["event"] == "StartUp":
        this.cargo.updateCargo(state["Cargo"], "Unknown", "Unknown")
        if len(state["Cargo"]) != 0:
            this.tipLabel.config(text="Some commodities were loaded before EDMC started up. Please make sure to have EDMC running when you pick up cargo for optimal function.")