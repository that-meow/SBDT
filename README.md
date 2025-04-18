# SBDT
Station Builder Delivery Tracker

This plugin for EDMC allows for automatic updates of delivery data on the https://station-builder.free.nf/ website.

Installation:
Download the ZIP file through GitHub (Code -> Download ZIP), then extract the SBDT-main folder into EDMC's plugin folder (File -> Plugins -> Open Plugin Folder).
After this, restart EDMC, and the plugin will load automatically together with the app.

Usage:
When the Delivery Tracker successfully loads up, it'll show the name of the plugin ("Delivery Tracker") and the text "Deliveries will show up here."
If EDMC is loaded while the ship's cargo is not empty, it'll display a warning message. EDMC can't see where you've bought the cargo, so if you load from a carrier, it can't register a carrier delivery.

Once you load new cargo, you may notice that the GUI doesn't update. The text only changes when a delivery is completed, meaning the cargo has been delivered to the destination station (may change this, if someone requests it).

After you sell cargo, in a few moments, the deliveries should appear. Press the "Send" button to send them to the website. After pressing "Send", the button is deactivated until a delivery has been successfully sent (this may be an issue, if the website doesn't respond properly).

You may also choose to check the "Send automatically" checkbox, which will send the deliveries whenever you charge your FSD. This also deactivates the "Send" button.
