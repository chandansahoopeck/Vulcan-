from src.services.request.request import Request


class Mapper:
    """Maps the query from snow to request objects"""

    @classmethod
    def map_data(cls, data: dict):
        """Loops on the dictionary retreived from snow and maps it to request objects."""
        requests = []
        for ritm in data["result"].keys():
            value = data["result"][ritm]
            try:
                if value["VM build type"] == "VRA cloud VM":
                    value["OS"] = (
                        value["Database Version"]
                        if value.get("Is this a Database Server?", "") == "MS SQL"
                        else value["OS"]
                    )
                    requests.append(
                        Request(
                            value["number"],
                            ritm,
                            value["Server Name"],
                            value["Classification"],
                            value["employee_number"],
                            value["Business Unit Supported"],
                            str(value["Server Name"]).split("-")[0],
                            value["Data Disk"],
                            value["Amount of RAM"],
                            value["CPU's"],
                            value["OS"],
                            value["Location"],
                        )
                    )
            except:
                pass
        return requests
