from abc import ABC, abstractmethod


class BaseAnalysisStrategy(ABC):
    @abstractmethod
    def analyse_call(self, audio_file_data: bytes) -> dict:
        pass
