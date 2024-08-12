from langchain.schema.embeddings import Embeddings
from typing import List
import time
import numpy as np
import tritonclient.http


class TritonHFEmbeddings(Embeddings):
    def __init__(
        self,
        triton_host=None,
        triton_port=8000,
        triton_model_name=None,
        triton_model_version=None,
    ) -> None:
        super().__init__()

        # default values
        if triton_host is None:
            triton_host = "triton"
        if triton_model_name is None:
            triton_model_name = "transformer_tensorrt_inference"
        if triton_model_version is None:
            triton_model_version = "1"

        self.triton_url = f"{triton_host}:{triton_port}"
        self.triton_model_name = triton_model_name
        self.triton_model_version = triton_model_version

    def _embed_with_triton(self, query: List[str]) -> List[List[float]]:
        triton_client = tritonclient.http.InferenceServerClient(
            url=self.triton_url, verbose=False
        )

        triton_batch_size = len(query)
        triton_inputs = []
        triton_outputs = []
        triton_text_input = tritonclient.http.InferInput(
            name="TEXT", shape=(triton_batch_size,), datatype="BYTES"
        )
        triton_text_input.set_data_from_numpy(np.asarray(query, dtype=object))
        triton_inputs.append(triton_text_input)
        triton_outputs.append(
            tritonclient.http.InferRequestedOutput("output", binary_data=False)
        )

        inference_results = triton_client.infer(
            model_name=self.triton_model_name,
            model_version=self.triton_model_version,
            inputs=triton_inputs,
            outputs=triton_outputs,
        )
        # triton_response = inference_results.get_response()
        # embedded_query = triton_response['outputs'][0]['data']
        embedded_query = inference_results.as_numpy("output").tolist()
        return embedded_query

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if len(texts) > 16:
            raise ValueError(f"Max batch size 16 is less than size of input batch: {len(texts)}")

        """Embed search docs."""
        start = time.perf_counter()

        embedded_query = self._embed_with_triton(texts)

        end = time.perf_counter()
        print(f"Triton Embed Texts [{len(texts)}] | Total Time: [{(end - start) * 1000} ms]")

        return embedded_query

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        start = time.perf_counter()

        embedded_query = self._embed_with_triton([text])

        end = time.perf_counter()
        print(f"Triton Embed Query [{text}] | Total Time: [{(end - start) * 1000} ms]")

        # unpack list of list to just a list
        return embedded_query[0]