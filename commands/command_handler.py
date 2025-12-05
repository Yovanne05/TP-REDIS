import requests
from widgets.message_box import MessageBox


class CommandHandler:
    def __init__(self, app):
        self.app = app

    def get_commands(self):
        return {
            "username": self.cmd_username,
            "channel": self.cmd_channel,
            "server": self.cmd_server,
            "weather": self.cmd_weather,
        }

    async def cmd_username(self, args: str, conversation_box) -> None:
        if args:
            self.app.username = args
            await conversation_box.mount(
                MessageBox(
                    f"Nom d'utilisateur changé en: {self.app.username}",
                    "INFO : ",
                )
            )

    async def cmd_channel(self, args: str, conversation_box) -> None:
        if args:
            self.app.conversation.change_channel(args)
            self.app.update_subtitle()
            self.app.listen()
            await conversation_box.mount(
                MessageBox(
                    f"Canal changé en: {args}",
                    "INFO : ",
                )
            )

    async def cmd_server(self, args: str, conversation_box) -> None:
        if args:
            parts = args.split(":")
            new_host = parts[0]
            new_port = int(parts[1]) if len(parts) > 1 else 6379
            try:
                self.app.conversation.change_server(new_host, new_port)
                self.app.update_subtitle()
                self.app.listen()
                await conversation_box.mount(
                    MessageBox(
                        f"Serveur changé en: {new_host}:{new_port}",
                        "INFO : ",
                    )
                )
            except Exception as e:
                await conversation_box.mount(
                    MessageBox(
                        f"Erreur de connexion au serveur: {str(e)}",
                        "ERREUR : ",
                    )
                )

    async def cmd_weather(self, args: str, conversation_box) -> None:
        if not args:
            await conversation_box.mount(
                MessageBox(
                    "Usage: /weather <ville>",
                    "ERREUR : ",
                )
            )
            return

        try:
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={args}&count=1&language=fr&format=json"
            geo_response = requests.get(geocoding_url, timeout=5)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if "results" not in geo_data or not geo_data["results"]:
                await conversation_box.mount(
                    MessageBox(
                        f"Ville '{args}' introuvable",
                        "ERREUR : ",
                    )
                )
                return

            location = geo_data["results"][0]
            latitude = location["latitude"]
            longitude = location["longitude"]
            city_name = location["name"]
            country = location.get("country", "")

            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={latitude}&longitude={longitude}"
                f"&current_weather=true"
            )

            weather_response = requests.get(weather_url, timeout=5)
            weather_response.raise_for_status()

            weather_data = weather_response.json()
            current = weather_data["current_weather"]
            temp = current["temperature"]

            weather_info = f"{city_name}, {country}: {temp}°C"

            await conversation_box.mount(
                MessageBox(
                    weather_info,
                    "MÉTÉO : ",
                )
            )
        except Exception as e:
            await conversation_box.mount(
                MessageBox(
                    f"Impossible de récupérer la météo: {str(e)}",
                    "ERREUR : ",
                )
            )
