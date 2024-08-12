import time 
import numpy as np
import tritonclient.http
import argparse
import json


def embed_query(triton_client, triton_model_name, triton_model_version, query):
    start = time.perf_counter()

    # add required prefix to queries for e5
    if isinstance(query, str):
        query = ["query: " + query]
    else:  # list of strings
        query = ["query: " + x for x in query]

    triton_batch_size = len(query)
    triton_inputs = []
    triton_outputs = []
    triton_text_input = tritonclient.http.InferInput(
        name="TEXT", shape=(triton_batch_size,), datatype="BYTES")
    triton_text_input.set_data_from_numpy(
        np.asarray(query, dtype=object))
    triton_inputs.append(triton_text_input)
    triton_outputs.append(tritonclient.http.InferRequestedOutput(
        'output', binary_data=False))

    inference_results = triton_client.infer(model_name=triton_model_name, model_version=triton_model_version,
                                  inputs=triton_inputs, outputs=triton_outputs)
    # triton_response = inference_results.get_response()
    # embedded_query = triton_response['outputs'][0]['data']
    embedded_query = inference_results.as_numpy('output')

    end = time.perf_counter()
    print(f"Triton (Total Time): {(end - start) * 1000} ms")

    return embedded_query, (end - start) * 1000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("query")
    parser.add_argument("nruns")
    args = parser.parse_args()
    host = args.host
    
    query = args.query
    query = json.loads(query)
    
    nruns = args.nruns
    nruns = int(nruns)

    triton_url = f"{host}:8000"
    triton_model_name = "transformer_tensorrt_inference"
    triton_model_version = "1"

    # Triton setup
    triton_client = tritonclient.http.InferenceServerClient(url=triton_url, verbose=False)
    assert triton_client.is_model_ready(
        model_name=triton_model_name, 
        model_version=triton_model_version
    )

    total_ms = 0.0
    for _ in range(nruns):
        embedded_query, ms = embed_query(triton_client, triton_model_name, triton_model_version, query)
        total_ms += ms

    print(embedded_query)
    print(embedded_query.shape)
    print(f"Average time elapsed over {nruns} runs: {total_ms / nruns} ms")

if __name__ == "__main__":
    main()
