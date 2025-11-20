"""Test core functionality"""

import asyncio

from core.channel_manager import ChannelManager

from core.alert_system import AlertSystem



async def test():

    # Test alert system

    alert_system = AlertSystem()

    is_alert, keywords, priority = alert_system.check_for_alerts(

        "Mayday, mayday, we need emergency assistance!"

    )

    print(f"Alert detected: {is_alert}, Keywords: {keywords}, Priority: {priority}")

    

    # Test channel manager

    channel_manager = ChannelManager()

    status = channel_manager.get_channel_status()

    print(f"Channels: {list(status.keys())}")



if __name__ == "__main__":

    asyncio.run(test())

