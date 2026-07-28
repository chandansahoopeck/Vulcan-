import json

from src.services.vra.vra import Vra


class Request:
    def __init__(
        self,
        number,
        ritm,
        servername,
        classification,
        application_owner,
        business_unit,
        sitecode,
        memory,
        ram,
        cpu,
        os,
        location_id,
    ) -> None:
        self.number = number
        self.ritm = ritm
        self.servername = str(servername).lower()
        self.__classification = classification
        self.owner = application_owner
        self.__bu = business_unit
        self.sitecode = str(sitecode).lower()
        self.__memory = memory
        self.__ram = ram
        self.__cpu = cpu
        self.__os = os
        self.location_id = location_id
        self.set_properties()

    def all_values(self):
        self.classification = self.__classification
        self.bu = self.__bu
        self.memory = self.__memory
        self.ram = self.__ram
        self.cpu = self.__cpu
        self.os = self.__os
        srv_list = str(self.servername).split("-")
        self.appname = srv_list[2].split(".")[0]
        description_mapping = self.__load_mapping("./src/constants/map/description.json")
        self.description = f"{str(description_mapping[self.os]).replace('[RITM]', self.ritm)}"
        # set the activation license for linux
        if str(self.os).lower().startswith("windows"):
            self.license = None
            self.domain = "ad.shared"
            self.groups = ""
            self.region = ""
        else:
            license_mapping = self.__load_mapping("./src/constants/map/license.json")
            self.license = license_mapping[self.os]
            self.domain = "wdc.com"
            groups_mapping = self.__load_mapping("./src/constants/map/groups.json")
            self.groups = groups_mapping[str(self.sitecode).lower()]
            region_mapping = self.__load_mapping("./src/constants/map/region.json")
            self.region = region_mapping[str(self.sitecode).lower()]

    def __str__(self) -> str:
        return f"Vra request {self.number} By {self.owner}: server: {self.servername}, sitecode: {self.sitecode}"

    def __load_mapping(self, file):
        with open(file) as f:
            data = json.load(f)
        return data

    def set_properties(self):
        """Set the properties mapping from servicenow to vra per the map files in contants"""
        try:
            # app name
            srv_list = str(self.servername).split("-")
            self.appname = srv_list[2].split(".")[0]
            # set the classification
            classification_mapping = self.__load_mapping("./src/constants/map/classification.json")
            self.classification = classification_mapping[self.__classification]
            if not str(srv_list[1]).lower().endswith("q") and self.__classification == "QA_TEST":
                classification_mapping = self.__load_mapping(
                    "./src/constants/map/classification.json"
                )
                self.classification = classification_mapping["test"]
            # set the business unit mapping
            bu_mapping = self.__load_mapping("./src/constants/map/bu.json")
            self.bu = bu_mapping[self.__bu]
            # set the disk space mapping
            memory_mapping = self.__load_mapping("./src/constants/map/memory.json")
            self.memory = memory_mapping[self.__memory]
            # set the ram mapping
            ram_mapping = self.__load_mapping("./src/constants/map/ram.json")
            self.ram = ram_mapping[self.__ram]
            # set the amount of cpu
            cpu_mapping = self.__load_mapping("./src/constants/map/cpu.json")
            self.cpu = cpu_mapping[self.__cpu]
            # set the os mapping
            os_mapping = self.__load_mapping("./src/constants/map/os.json")
            self.os = os_mapping[self.__os]
            # set the description
            description_mapping = self.__load_mapping("./src/constants/map/description.json")
            self.description = f"{str(description_mapping[self.os]).replace('[RITM]', self.ritm)}"
            # set the activation license for linux
            if str(self.os).lower().startswith("windows"):
                self.license = None
                self.domain = "ad.shared"
                self.groups = ""
                self.region = ""
            else:
                license_mapping = self.__load_mapping("./src/constants/map/license.json")
                self.license = license_mapping[self.__os]
                self.domain = "wdc.com"
                groups_mapping = self.__load_mapping("./src/constants/map/groups.json")
                self.groups = groups_mapping[str(self.sitecode).lower()]
                region_mapping = self.__load_mapping("./src/constants/map/region.json")
                self.region = region_mapping[str(self.sitecode).lower()]

        except Exception as e:
            print(str(e))
            # raise ValueError(str(e))
