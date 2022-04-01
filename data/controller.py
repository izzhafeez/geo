from gsheets import Sheets
import pandas as pd

class Controller:
	SHEET_ID = "1M9Ujc54yZZPlxOX3yxWuqcuJOxzIrDYz4TAFx8ifB8c"

	@staticmethod
	def get(name: str) -> pd.DataFrame:
		sheets = Sheets.from_files('client_secrets.json','~/storage.json')[Controller.SHEET_ID]
		return sheets.find(name).to_frame()
