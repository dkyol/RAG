from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi


description = """The **NVIDIA DLI Chunking API** is developed by the Developer Programs Solutions Engineering team.
It is intended to provide common access to various strategies for chunking of text and HTML documents. It is built with FastAPI.

## Usage
### ❗To use these docs, click "Try it out", pick your example from the dropdown, and then click "Execute".

### ❗For the **chunking** endpoint, there are three mandatory values in your request JSON body: **strategy**, **input_type**, and **input_str**.

- Accepted values for chunking **strategy** are: "sentence", "paragraph", "heading_section", and "heading_section_paragraph".

- Accepted values for chunking **input_type** are: "text" and "html".
"""


tags_metadata = [
    {
        "name": "chunking",
        "description": "Primary API endpoint.",
    },
    {
        "name": "health",
        "description": "Health check. Returns code 200 response if application is running.",
    },
]


def clear_openapi_responses(app):
    def custom_openapi():
        if not app.openapi_schema:
            app.openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                terms_of_service=app.terms_of_service,
                contact=app.contact,
                license_info=app.license_info,
                routes=app.routes,
                tags=app.openapi_tags,
                servers=app.servers,
            )
            for _, method_item in app.openapi_schema.get("paths").items():
                for _, param in method_item.items():
                    responses = param.get("responses")
                    responses.clear()
        return app.openapi_schema

    app.openapi = custom_openapi


example_raw_text = """Hello this is sentence 1. And this is sentence 2?
What about sentence 3? And sentence 4!

And who could forget sentence 5... Maybe sentence 6 could.

```
print("Code in sentence 7");

    # Code in sentence 8;
```

Sentence 9 has no code.
"""

example_html = """<div class="entry-content">
<p>Many CUDA applications running on multi-GPU platforms usually use a single GPU for their compute needs. In such scenarios, a performance penalty is paid by applications because CUDA has to enumerate/initialize all the GPUs on the system. If a CUDA application does not require other GPUs to be visible and accessible, you can launch such applications by isolating the unwanted GPUs from the CUDA process and eliminating unnecessary initialization steps.&nbsp;</p>
<p>This post discusses the various methods to accomplish this and their performance benefits.</p>
<h2 class="wp-block-heading">GPU isolation</h2>
<p>GPU isolation can be achieved on Linux systems by using Linux tools like <code>cgroups</code>. In this section, we first discuss a lower-level approach and then a higher-level possible approach.</p>
<p>Another method exposed by CUDA to isolate devices is the use of <code>CUDA_VISIBLE_DEVICES</code>. Although functionally similar, this approach has limited initialization performance gains compared to the <code>cgroups</code> approach.</p>
<h3 class="wp-block-heading">Isolating GPUs using cgroups V1</h3>
<p>Control groups provide a mechanism for aggregating or partitioning sets of tasks and all their future children into hierarchical groups with specialized behavior. You can use <code>cgroups</code> to control which GPUs are visible to a CUDA process. This ensures that only the GPUs that are needed by the CUDA process are made available to it.</p>
<p>The following code provides a low-level example of how to employ <code>cgroups</code> and fully isolate a GPU to a single process. Be aware that you will likely have to run these commands in a root shell to work properly. We show a more convenient, higher-level utility later in this post.</p>
<div class="wp-block-syntaxhighlighter-code "><div><div id="highlighter_297539" class="syntaxhighlighter nogutter  cpp"><table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td class="code"><div class="container"><div class="line number1 index0 alt2"><code class="cpp preprocessor"># Create a mountpoint for the cgroup hierarchy as root</code></div><div class="line number2 index1 alt1"><code class="cpp plain">$&gt; cd /mnt</code></div><div class="line number3 index2 alt2"><code class="cpp plain">$&gt; mkdir cgroupV1Device</code></div><div class="line number4 index3 alt1">&nbsp;</div><div class="line number5 index4 alt2"><code class="cpp preprocessor"># Use mount command to mount the hierarchy and attach the device subsystem to it</code></div><div class="line number6 index5 alt1"><code class="cpp plain">$&gt; mount -t cgroup -o devices devices cgroupV1Device</code></div><div class="line number7 index6 alt2"><code class="cpp plain">$&gt; cd cgroupV1Device</code></div><div class="line number8 index7 alt1"><code class="cpp preprocessor"># Now create a gpu subgroup directory to restrict/allow GPU access</code></div><div class="line number9 index8 alt2"><code class="cpp plain">$&gt; mkdir gpugroup</code></div><div class="line number10 index9 alt1"><code class="cpp plain">$&gt; cd gpugroup</code></div><div class="line number11 index10 alt2"><code class="cpp preprocessor"># in the gpugroup, you will see many cgroupfs files, the ones that interest us are tasks, device.deny and device.allow</code></div><div class="line number12 index11 alt1"><code class="cpp plain">$&gt; ls gpugroup</code></div><div class="line number13 index12 alt2"><code class="cpp plain">tasks&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; devices.deny&nbsp;&nbsp;&nbsp;&nbsp; devices.allow</code></div><div class="line number14 index13 alt1">&nbsp;</div><div class="line number15 index14 alt2"><code class="cpp preprocessor"># Launch a shell from where the CUDA process will be executed. Gets the shells PID</code></div><div class="line number16 index15 alt1"><code class="cpp plain">$&gt; echo $$</code></div><div class="line number17 index16 alt2">&nbsp;</div><div class="line number18 index17 alt1"><code class="cpp preprocessor"># Write this PID into the tasks files in the gpugroups folder</code></div><div class="line number19 index18 alt2"><code class="cpp plain">$&gt; echo &lt;PID&gt; tasks</code></div><div class="line number20 index19 alt1">&nbsp;</div><div class="line number21 index20 alt2"><code class="cpp preprocessor"># List the device numbers of nvidia devices with the ls command</code></div><div class="line number22 index21 alt1"><code class="cpp plain">$&gt; ls -l /dev/nvidia*</code></div><div class="line number23 index22 alt2"><code class="cpp plain">crw-rw-rw- 1 root root 195,&nbsp;&nbsp; 0 Jul 11 14:28 /dev/nvidia0</code></div><div class="line number24 index23 alt1"><code class="cpp plain">crw-rw-rw- 1 root root 195,&nbsp;&nbsp; 0 Jul 11 14:28 /dev/nvidia1</code></div><div class="line number25 index24 alt2">&nbsp;</div><div class="line number26 index25 alt1"><code class="cpp preprocessor"># Assuming that you only want to allow the CUDA process to access GPU0, you deny the CUDA process access to GPU1 by writing the following command to devices.deny</code></div><div class="line number27 index26 alt2"><code class="cpp plain">$&gt; echo </code><code class="cpp string">'c 195:1 rmw'</code> <code class="cpp plain">&gt; devices.deny</code></div><div class="line number28 index27 alt1">&nbsp;</div><div class="line number29 index28 alt2"><code class="cpp preprocessor"># Now GPU1 will not be visible to The CUDA process that you launch from the second shell.</code></div><div class="line number30 index29 alt1"><code class="cpp preprocessor"># To provide the CUDA process access to GPU1, we should write the following to devices.allow</code></div><div class="line number31 index30 alt2">&nbsp;</div><div class="line number32 index31 alt1"><code class="cpp plain">$&gt; echo </code><code class="cpp string">'c 195:1 rmw'</code> <code class="cpp plain">&gt; devices.allow</code></div></div></td></tr></tbody></table></div></div></div>
<p>When you are done with the tasks, unmount the <code>/cgroupV1Device</code> folder with the umount command.</p>
<div class="wp-block-syntaxhighlighter-code "><div><div id="highlighter_908156" class="syntaxhighlighter nogutter  cpp"><table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td class="code"><div class="container"><div class="line number1 index0 alt2"><code class="cpp plain">umount /mnt/cgroupV1Device</code></div></div></td></tr></tbody></table></div></div></div>
<p>To allow or deny the user access to any other GPUs on the system, write those GPU numbers to the appropriate file. Here’s an example of denying access to only GPU5 and GPU6 on a multi-GPU system.</p>
<p>In the <code>/gpugroup</code> folder created earlier, write the PID of the shell from where the CUDA process is to be launched into the <code>tasks</code> file:</p>
<div class="wp-block-syntaxhighlighter-code "><div><div id="highlighter_142290" class="syntaxhighlighter nogutter  cpp"><table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td class="code"><div class="container"><div class="line number1 index0 alt2"><code class="cpp plain">$&gt; echo &lt;PID&gt; tasks</code></div></div></td></tr></tbody></table></div></div></div>
<p>Now add GPU5 and GPU6 to the denied list:</p>
<div class="wp-block-syntaxhighlighter-code "><div><div id="highlighter_642618" class="syntaxhighlighter nogutter  cpp"><table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td class="code"><div class="container"><div class="line number1 index0 alt2"><code class="cpp plain">$&gt; echo </code><code class="cpp string">'c 195:5 rmw'</code> <code class="cpp plain">&gt; devices.deny</code></div><div class="line number2 index1 alt1"><code class="cpp plain">$&gt; echo </code><code class="cpp string">'c 195:6 rmw'</code> <code class="cpp plain">&gt; devices.deny</code></div></div></td></tr></tbody></table></div></div></div>
<p>At this point, the CUDA process can’t see or access the two GPUs. To enable only specific GPUs to a CUDA process, those GPUs should be added to the <code>devices.allow</code> file and the rest of the GPUs should be added to the <code>devices.deny</code> file.&nbsp;</p>
<p>The access controls apply per process. Multiple processes can be added to the <code>tasks</code> file to propagate the same controls to more than one process.</p>
<h3 class="wp-block-heading">Isolating GPUs using the bubblewrap utility</h3>
<p>The bubblewrap utility (bwrap) is a higher-level utility available for sandboxing and access control in Linux operating systems, which can be used to achieve the same effect as the solution presented earlier. You can use this to conveniently restrict or allow access to specific GPUs from a CUDA process:</p>
<div class="wp-block-syntaxhighlighter-code "><div><div id="highlighter_148145" class="syntaxhighlighter nogutter  cpp"><table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td class="code"><div class="container"><div class="line number1 index0 alt2"><code class="cpp preprocessor"># install bubblewrap utility on Debian-like systems</code></div><div class="line number2 index1 alt1"><code class="cpp plain">$&gt;sudo apt-get install -y bubblewrap</code></div><div class="line number3 index2 alt2">&nbsp;</div><div class="line number4 index3 alt1"><code class="cpp preprocessor"># create a simple shell script that uses bubblewap for binding the required GPU to the launched process</code></div><div class="line number5 index4 alt2">&nbsp;</div><div class="line number6 index5 alt1"><code class="cpp preprocessor">#!/bin/sh</code></div><div class="line number7 index6 alt2"><code class="cpp preprocessor"># bwrap.sh</code></div><div class="line number8 index7 alt1"><code class="cpp plain">GPU=$1;shift&nbsp;&nbsp; # 0, 1, 2, 3, ..</code></div><div class="line number9 index8 alt2"><code class="cpp keyword bold">if</code> <code class="cpp plain">[ </code><code class="cpp string">"$GPU"</code> <code class="cpp plain">= </code><code class="cpp string">""</code> <code class="cpp plain">]; then echo </code><code class="cpp string">"missing arg: gpu id"</code><code class="cpp plain">; </code><code class="cpp functions bold">exit</code> <code class="cpp plain">1; fi</code></div><div class="line number10 index9 alt1"><code class="cpp plain">bwrap \</code></div><div class="line number11 index10 alt2"><code class="cpp spaces">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code><code class="cpp plain">--bind / / \</code></div><div class="line number12 index11 alt1"><code class="cpp spaces">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code><code class="cpp plain">--dev /dev --dev-bind /dev/nvidiactl /dev/nvidiactl --dev-bind /dev/nvidia-uvm /dev/nvidia-uvm&nbsp; \</code></div><div class="line number13 index12 alt2"><code class="cpp spaces">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code><code class="cpp plain">--dev-bind /dev/nvidia$GPU /dev/nvidia$GPU \</code></div><div class="line number14 index13 alt1"><code class="cpp spaces">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code><code class="cpp string">"$@"</code></div><div class="line number15 index14 alt2">&nbsp;</div><div class="line number16 index15 alt1">&nbsp;</div><div class="line number17 index16 alt2"><code class="cpp preprocessor"># Launch the CUDA process with the bubblewrap utility to only allow access to a specific GPU while running</code></div><div class="line number18 index17 alt1"><code class="cpp plain">$&gt; ./bwrap.sh 0 ./test_cuda_app &lt;args&gt;</code></div></div></td></tr></tbody></table></div></div></div>
<p>More than one GPU can be exposed to a CUDA process by extending the <code>dev-bind</code> option in the code example.</p>
<h2 class="wp-block-heading">Performance benefits of GPU isolation&nbsp;</h2>
<p>In this section, we compare the performance of the CUDA driver initialization API (cuInit) with and without GPU isolation, measured over 256 iterations. The APIs are being run on an x86-based machine with four A100 class GPUs.</p>
<div class="wp-block-image">
<figure class="aligncenter size-full"><img decoding="async" width="1200" height="742" src="https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance.png" alt="Bar graph shows the performance of cuInit API running on an A104 system with and without GPU isolation using cgroups. The bar on the left shows the performance of cuInit when only a single GPU is exposed to the calling CUDA process via cgroups (~65 ms). The bar on the right shows the performance of cuInit when all four GPUs on the system are made available to the CUDA process (225 ms)." class="wp-image-75547" title="Chart" srcset="https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance.png 1200w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-300x186.png 300w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-625x386.png 625w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-179x111.png 179w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-768x475.png 768w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-645x399.png 645w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-485x300.png 485w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-146x90.png 146w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-362x224.png 362w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-178x110.png 178w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/CUDA-initialisation-performance-1024x633.png 1024w" sizes="(max-width: 1200px) 100vw, 1200px"><figcaption class="wp-element-caption"><em>Figure 1. CUDA initialisation performance comparison between a </em>cgroup<em>-constrained process and the default scenario on a four-GPU test system</em></figcaption></figure></div>
<h2 class="wp-block-heading">Summary</h2>
<p>GPU isolation using <code>cgroups</code> offers you the option of improving CUDA initialization times in a limited number of use cases where all the GPUs on the system are not required to be used by a given CUDA process.</p>
<p>For more information, see the following resources:</p>
<ul>
<li><a href="https://docs.kernel.org/admin-guide/cgroup-v1/index.html" data-wpel-link="external" target="_blank" rel="follow external noopener">Control Groups version 1 — The Linux Kernel documentation</a></li>
<li><a href="https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__INITIALIZE.html" data-wpel-link="internal" target="_self" rel="noopener noreferrer">cuInit</a></li>
</ul>
</div>"""

example_html2 = """<div class="entry-content">
<p>At the core of understanding people correctly and having natural conversations is automatic speech recognition (ASR). To make customer-led voice assistants and automate customer service interactions over the phone, companies must solve the unique challenge of gaining a caller’s trust through qualities such as understanding, empathy, and clarity.</p>
<p>Telephony-bound voice is inherently challenging from a speech recognition perspective. Background noise, poor call quality, and various dialects and accents make understanding a caller’s words difficult. Traditional language understanding systems have limited support for voice in general, and how a person speaks differs fundamentally from how they type or text.</p>
<p>In this post, we discuss <a href="https://poly.ai/" data-wpel-link="external" target="_blank" rel="follow external noopener">PolyAI</a>’s exploration journey with third-party, out-of-the-box, and in-house customized <a href="https://www.nvidia.com/en-us/ai-data-science/products/riva/" data-wpel-link="internal" target="_self" rel="noopener noreferrer">NVIDIA Riva </a>ASR solutions. The goal is to deliver voice experiences that let callers speak however they like, providing helpful and natural responses at every turn of the conversation.&nbsp; The in-house fine-tuned Riva ASR models resulted in notable accuracy improvement on a variety of different validation real-world customer call datasets.</p>
<h2 class="wp-block-heading">Out-of-the-box ASR challenges for effective customer interactions</h2>
<p>Out-of-the-box ASR tools are typically prepared for non-noisy environments and speakers who clearly enunciate and have expected accents. These systems can’t predict what a caller will say, how they might say it, or their speaking tempo. While out-of-the-box solutions can be useful, they can’t be tailored to specific business needs and objectives.&nbsp;</p>
<p>To achieve accurate voice assistants that handle customer interactions efficiently, organizations require an ASR system that can be fine-tuned to significantly improve word error rate (WER).</p>
<h2 class="wp-block-heading">Advantages and challenges of building an in-house ASR solution</h2>
<p>To truly understand people from different places, with different accents, and in noisy environments, conversational systems can use multiple ASR systems, phoneme matching, biasing keywords, and post-processing tools.&nbsp;</p>
<p>The machine learning team at PolyAI rigorously tested numerous ASR systems, often on multiple models, and applied spoken language understanding (SLU) principles to improve transcription accuracy (Figure 1). This work significantly improved the accuracy of speech recognition in real customer phone calls.&nbsp;</p>
<p>Optimizing the caller experience further required the development of an in-house solution.&nbsp;</p>
<div class="wp-block-image">
<figure class="aligncenter size-full"><img decoding="async" width="1527" height="662" src="https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack.png" alt="Diagram shows stack components: ASR systems, phoneme matching, biasing keywords, and post-processing tools." class="wp-image-75797" srcset="https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack.png 1527w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-300x130.png 300w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-625x271.png 625w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-179x78.png 179w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-768x333.png 768w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-645x280.png 645w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-500x217.png 500w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-160x69.png 160w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-362x157.png 362w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-254x110.png 254w, https://developer-blogs.nvidia.com/wp-content/uploads/2023/12/polyai-tech-stack-1024x444.png 1024w" sizes="(max-width: 1527px) 100vw, 1527px"><figcaption class="wp-element-caption"><em>Figure 1. PolyAI tech stack</em></figcaption></figure></div>
<p>The PolyAI tech stack enables voice assistants to accurately understand alphanumeric inputs and people from different places, with different accents, and in noisy environments.</p>
<p>Developing an in-house solution approach offers the following advantages:</p>
<ul>
<li><strong>Better accuracy and performance</strong> with flexible fine-tuning of model parameters on extensive data and voice activity detector (VAD) adaptation for the specific ways in which people talk with the system.</li>
<li><strong>Full compliance </strong>with a bring-your-own-cloud (BYOC) approach that delivers the model and the whole conversational system to clients with zero data transfers to third-party providers.</li>
</ul>
<p>With great benefits comes a unique set of challenges. Building an in-house solution requires heavy investment in the following areas:</p>
<ul>
<li><strong>Expensive pretraining data</strong>: Most models require large quantities of good quality, annotated, pretraining data.&nbsp;</li>
<li><strong>Latency optimization</strong>: This area is often overlooked in the research process. Contrary to chat conversation, voice conversation operates on milliseconds. Every millisecond counts. Adding latency at the start of the conversation gives even less time when calling the large language models (LLM) or text-to-speech (TTS) models.</li>
</ul>
<h2 class="wp-block-heading">Choosing and finetuning ASR models for an in-house solution</h2>
<p>After a substantial search for an ASR solution that addresses building in-house solution challenges, PolyAI decided to use <a href="https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html" data-wpel-link="internal" target="_self" rel="noopener noreferrer">NVIDIA Riva</a> for the following reasons:&nbsp;</p>
<ul>
<li><strong>Cutting-edge accuracy of pretrained models</strong> trained on a substantial volume of conversational speech data.&nbsp;</li>
<li><strong>Enhanced accuracy with full model customization</strong>, including <a href="https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-customizing.html#fine-tuning-existing-models" data-wpel-link="internal" target="_self" rel="noopener noreferrer">acoustic model customization </a>for different accents, noisy environments, or poor audio quality.</li>
<li><strong>High inference performance </strong>based on tight coupling with <a href="https://www.nvidia.com/en-us/ai-data-science/products/triton-inference-server/" data-wpel-link="internal" target="_self" rel="noopener noreferrer">NVIDIA Triton Inference Server</a> and battle-tested to handle machine learning servicing.</li>
</ul>
<p>Initial trials with an in-house ASR model provided valuable insights into the fine-tuning process. This led to the development of a robust and flexible fine-tuning methodology, incorporating diverse validation sets to ensure optimal performance.</p>
<h2 class="wp-block-heading">Conversational system for testing out-of-the-box and in-house ASR solutions&nbsp;</h2>
<p>Typical conversational systems use public switched telephone networks (PSTN) or session initiation protocol (SIP) connections to transfer calls into the tech stack.&nbsp;</p>
<p>Call information from these systems is then sent to third-party ASR cloud service providers or in-house ASR solutions. For PolyAI’s testing of ASR solutions (Figure 2), after a call is transcribed, it is sent to a PolyAI voice assistant, where natural language models generate a response. The response is then transferred back into the audio wave through in-house TTS or third-party providers.&nbsp;</p>
<div class="wp-block-image">
<figure class="aligncenter size-full"><img decoding="async" width="1999" height="1227" src="https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b.png" alt="Diagram includes a telephony gateway, audio gateway, natural language models, and text-to-speech." class="wp-image-76377" srcset="https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b.png 1999w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-300x184.png 300w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-625x384.png 625w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-179x110.png 179w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-768x471.png 768w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-1536x943.png 1536w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-645x396.png 645w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-489x300.png 489w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-147x90.png 147w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-362x222.png 362w, https://developer-blogs.nvidia.com/wp-content/uploads/2024/01/polyai-architecture-b-1024x629.png 1024w" sizes="(max-width: 1999px) 100vw, 1999px"><figcaption class="wp-element-caption"><em>Figure 2. PolyAI architecture for testing ASR solutions</em></figcaption></figure></div>
<h2 class="wp-block-heading">Creating a real-world ASR testing dataset</h2>
<p>PolyAI identified 20 hours of the most challenging conversations split equally between UK and US region calls to test the accuracy of third-party, out-of-the-box, and in-house ASR solutions. These were the calls with noisy environments and ones where other ASR models—in-house or third-party providers—had previously failed.&nbsp;&nbsp;</p>
<p>These failure calls varied from single-word utterances, such as ‘yes’ or ‘no’ answers, to much longer responses. PolyAI manually annotated them and established a word error rate (WER) below 1%, essential when dealing with fine-tuning ASR models.</p>
<h2 class="wp-block-heading">Notable accuracy improvement of an in-house customized ASR solution&nbsp;</h2>
<p>Fine-tuning two in-house ASR models using only 20 hours of data already resulted in a notable mean WER improvement for the US English model, reducing it by ~8.4% compared to the best model from CSP (Table 1). The importance of choosing the right model should be noted since different CSP out-of-the-box ASR models resulted in 44.51% mean WER.&nbsp;</p>
<p>Even more remarkable is that the WER median of in-house US English ASR solution reached 0%. This achievement was validated across various data sets, ensuring the fine-tuning was not overfitting a specific use case. This versatility allows the model to perform well across different projects where people use specific keywords, enabling the accurate understanding of particular phrases and enhancing overall median performance.</p>
<figure class="wp-block-table aligncenter is-style-stripes"><table><tbody><tr><td><strong>US English</strong></td><td><strong>Provider</strong></td><td><strong>Model</strong></td><td><strong>Language</strong></td><td><strong>WER Mean [%]</strong></td><td><strong>WER MEdian [%]</strong></td></tr><tr><td>0</td><td>Poly AI</td><td>Fine-Tuned</td><td>En-US</td><td><strong>20.32</strong></td><td><strong>0.00</strong></td></tr><tr><td>1</td><td>Poly AI</td><td>Fine-TUned</td><td>En-All</td><td>22.19</td><td>7.14</td></tr><tr><td>2</td><td>CSP</td><td>Best</td><td>En-US</td><td>22.22</td><td>7.69</td></tr><tr><td>9</td><td>CSP</td><td>Worst</td><td>En-US</td><td><strong>44.51</strong></td><td><strong>33.33</strong></td></tr></tbody></table><figcaption class="wp-element-caption"><em>Table 1. PolyAI in-house US English ASR solution achieved better accuracy with acoustic model fine-tunings than third-party out-of-the-box ASR</em></figcaption></figure>
<p>A similar pattern is observed with the UK English ASR solution (Table 2).&nbsp;</p>
<figure class="wp-block-table aligncenter is-style-stripes"><table><tbody><tr><td><strong>UK English</strong></td><td><strong>Provider</strong></td><td><strong>Model</strong></td><td><strong>Language</strong></td><td><strong>WER Mean [%]</strong></td><td><strong>WER MEdian [%]</strong></td></tr><tr><td>0</td><td>Poly AI</td><td>Fine-Tuned</td><td>En-UK</td><td><strong>20.99</strong></td><td><strong>8.33</strong></td></tr><tr><td>1</td><td>Poly AI</td><td>Fine-TUned</td><td>En-All</td><td>22.77</td><td>10.00</td></tr><tr><td>2</td><td>CSP</td><td>Best</td><td>En-UK</td><td>25.15</td><td>14.29</td></tr><tr><td>9</td><td>CSP</td><td>Worst</td><td>En-UK</td><td><strong>33.46</strong></td><td><strong>25.00</strong></td></tr></tbody></table><figcaption class="wp-element-caption"><em>Table 2. PolyAI in-house UK English ASR solution achieved better accuracy with acoustic model fine-tunings than third-party out-of-the-box ASR</em></figcaption></figure>
<p>Only 20 hours of fine-tuning data demonstrates the potential for further fine-tuning. More importantly, the in-house fine-tuned ASR model kept the same score when evaluated on a variety of different validation datasets as when it was in its original pretrained state.</p>
<h2 class="wp-block-heading">Summary</h2>
<p>For effectively automating customer interactions over the phone, fully customized ASR models play a pivotal role in solving the challenges of the voice channel, including background noise, poor call quality, and various dialects and accents. Dive deeper into PolyAI’s ASR transformative journey and explore the possibilities of speech AI and <a href="https://www.nvidia.com/en-us/ai-data-science/products/riva/" data-wpel-link="internal" target="_self" rel="noopener noreferrer">NVIDIA Riva</a> by checking out <a href="https://www.nvidia.com/en-us/events/speech-ai-day/" data-wpel-link="internal" target="_self" rel="noopener noreferrer">Speech AI Day</a> sessions.</p>
<p>PolyAI, part of <a href="https://www.nvidia.com/en-us/startups/" data-wpel-link="internal" target="_self" rel="noopener noreferrer">NVIDIA Inception</a>, provides a customer-led conversational platform for enterprises. To reimagine customer service with a best-in-class voice experience, see <a href="https://poly.ai/call-recordings/" data-wpel-link="external" target="_blank" rel="follow external noopener">PolyAI’s product</a> and <a href="https://poly.ai/request-a-demo/" data-wpel-link="external" target="_blank" rel="follow external noopener">sign up for a free trial</a>. Join the conversation on Speech AI in the <a href="https://forums.developer.nvidia.com/c/ai-data-science/deep-learning/riva/475" data-wpel-link="internal" target="_self" rel="noopener noreferrer">NVIDIA Riva forum</a>.</p>
</div>"""


class ChunkingRequest(BaseModel):
    strategy: str
    input_type: str
    input_str: str
    chunk_min_words: Optional[int] = 0
    chunk_overlap_words: Optional[int] = 0
    code_behavior: Optional[str] = None
    paragraph_delimeter: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None


chunking_examples = {
    "example00": {
        "summary": "Sentence chunking raw text with default parameters.",
        "description": "We chunk the text string by sentence. Since chunk_min_words and chunk_overlap_words are both 0 by default, each chunk "
        "will be a single sentence, with no overlap between chunks. " 
        "respect_code_boundaries is default code_behavior, meaning code sections cannot be combined with regular text.",
        "value": {
            "strategy": "sentence",
            "input_type": "text",
            "input_str": example_raw_text,
        },
    },
    "example01": {
        "summary": "Sentence chunking raw text with chunk_min_words=20 and chunk_overlap_words=10, respect code boundaries.",
        "description": "We chunk the text string by sentence. We add sentences until each chunk is at least 20 words if possible, with at least 10 words of overlap. "
        "respect_code_boundaries is default code_behavior, meaning code sections cannot be combined with regular text." ,
        "value": {
            "strategy": "sentence",
            "input_type": "text",
            "chunk_min_words": 20,
            "chunk_overlap_words": 10,
            "code_behavior": "respect_code_boundaries",
            "input_str": example_raw_text,
        },
    },
    "example02": {
        "summary": "Sentence chunking raw text with chunk_min_words=20 and chunk_overlap_words=10, ignore code boundaries.",
        "description": "We chunk the text string by sentence. We add sentences until each chunk is at least 20 words if possible, with at least 10 words of overlap. "
        "code_behavior is set to ignore_code_boundaries, meaning code sections will be combined with regular text. Only use this if you want to embed chunks containing a mix of " 
        "both code and regular text.",
        "value": {
            "strategy": "sentence",
            "input_type": "text",
            "chunk_min_words": 20,
            "chunk_overlap_words": 10,
            "code_behavior": "ignore_code_boundaries",
            "input_str": example_raw_text,
        },
    },
    "example03": {
        "summary": "Sentence chunking raw text with chunk_min_words=20 and chunk_overlap_words=10, remove code sections.",
        "description": "We chunk the text string by sentence. We add sentences until each chunk is at least 20 words if possible, with at least 10 words of overlap. "
        "remove_code_sections is non-default code_behavior. If we choose this mode, we remove code and store it as metadata. Use this if you want to preserve the code " 
        "sections in the chunk metadata but do not want to embed the actual text",
        "value": {
            "strategy": "sentence",
            "input_type": "text",
            "chunk_min_words": 20,
            "chunk_overlap_words": 10,
            "code_behavior": "remove_code_sections",
            "input_str": example_raw_text,
        },
    },
    "example04": {
        "summary": "Paragraph chunking raw text with default parameters.",
        "description": "We chunk the text string by paragraph. Since chunk_min_words and chunk_overlap_words are both 0 by default, each chunk "
        "will be a single paragraph, with no overlap between chunks. respect_code_boundaries is default code_behavior.",
        "value": {
            "strategy": "paragraph",
            "input_type": "text",
            "input_str": example_raw_text,
        },
    },
    "example05": {
        "summary": "Paragraph chunking raw text, remove code sections.",
        "description": "We chunk the text string by paragraph. Since chunk_min_words and chunk_overlap_words are both 0 by default, each chunk "
        "will be a single paragraph, with no overlap between chunks. code_behavior is set to remove_code_sections.",
        "value": {
            "strategy": "paragraph",
            "input_type": "text",
            "code_behavior": "remove_code_sections",
            "input_str": example_raw_text,
        },
    },
    "example06": {
        "summary": "Sentence chunking HTML with chunk_min_words=100 and chunk_overlap_words=20.",
        "description": "We chunk the HTML string by sentence. We add sentences until each chunk is at least 100 words if possible, with at least 20 words of overlap. " 
        "respect_code_boundaries is default code_behavior, meaning code sections cannot be combined with regular text.",
        "value": {
            "strategy": "sentence",
            "input_type": "html",
            "chunk_min_words": 100,
            "chunk_overlap_words": 20,
            "code_behavior": "respect_code_boundaries",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example07": {
        "summary": "Paragraph chunking HTML with chunk_min_words=250 and chunk_overlap_words=50, respect code boundaries.",
        "description": "We chunk the HTML string by paragraph. We add paragraphs until each chunk is 250 words if possible, with 50 words of overlap. "
        "respect_code_boundaries is default code_behavior, meaning code sections cannot be combined with regular text.",
        "value": {
            "strategy": "paragraph",
            "input_type": "html",
            "chunk_min_words": 250,
            "chunk_overlap_words": 50,
            "code_behavior": "respect_code_boundaries",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example08": {
        "summary": "Paragraph chunking HTML with chunk_min_words=250 and chunk_overlap_words=50, remove code sections.",
        "description": "We chunk the HTML string by paragraph. We add paragraphs until each chunk is 250 words if possible, with 50 words of overlap. "
        "code_behavior is set to remove_code_sections.",
        "value": {
            "strategy": "paragraph",
            "input_type": "html",
            "chunk_min_words": 250,
            "chunk_overlap_words": 50,
            "code_behavior": "remove_code_sections",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example09": {
        "summary": "Heading section chunking HTML.",
        "description": "We chunk the HTML string by heading sections. Note this method will always ignore code boundaries.",
        "value": {
            "strategy": "heading_section",
            "input_type": "html",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example10": {
        "summary": "Heading section sentence chunking HTML with chunk_min_words=60 and chunk_overlap_words=20, respect code boundaries.",
        "description": "We chunk the HTML string by sentences, keeping track of which heading section the sentence originated from. "
        "We add sentences until each chunk is at least 60 words if possible, with at least 20 words of overlap. "
        "respect_code_boundaries is default code_behavior, meaning code sections cannot be combined with regular text. " 
        "Important distinction is it does not treat headings as paragraphs themselves. They are returned in the "
        "heading_section_title field in the response JSON.",
        "value": {
            "strategy": "heading_section_sentence",
            "input_type": "html",
            "chunk_min_words": 60,
            "chunk_overlap_words": 20,
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example11": {
        "summary": "Heading section sentence chunking HTML with chunk_min_words=60 and chunk_overlap_words=20, remove code sections.",
        "description": "We chunk the HTML string by sentences, keeping track of which heading section the sentence originated from. "
        "We add sentences until each chunk is at least 60 words if possible, with at least 20 words of overlap. "
        "code_behavior is set to remove_code_sections. "
        "Important distinction is it does not treat headings as paragraphs themselves. They are returned in the "
        "heading_section_title field in the response JSON.",
        "value": {
            "strategy": "heading_section_sentence",
            "input_type": "html",
            "chunk_min_words": 60,
            "chunk_overlap_words": 20,
            "code_behavior": "remove_code_sections",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example12": {
        "summary": "Heading section paragraph chunking HTML with chunk_min_words=300 and chunk_overlap_words=0, respect code boundaries.",
        "description": "We chunk the HTML string by paragraphs, keeping track of which heading section the paragraph originated from. "
        "We add paragraphs until each chunk is at least 300 words if possible, with 0 words of overlap. "
        "respect_code_boundaries is default code_behavior, meaning code sections cannot be combined with regular text. " 
        "Important distinction is it does not treat headings as paragraphs themselves. They are returned in the "
        "heading_section_title field in the response JSON.",
        "value": {
            "strategy": "heading_section_paragraph",
            "input_type": "html",
            "chunk_min_words": 300,
            "chunk_overlap_words": 0,
            "code_behavior": "respect_code_boundaries",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example13": {
        "summary": "Heading section paragraph chunking HTML with chunk_min_words=300 and chunk_overlap_words=0, remove code sections.",
        "description": "We chunk the HTML string by paragraphs, keeping track of which heading section the paragraph originated from. "
        "We add paragraphs until each chunk is at least 300 words if possible, with 0 words of overlap. "
        "code_behavior is set to remove_code_sections. "
        "Important distinction is it does not treat headings as paragraphs themselves. They are returned in the "
        "heading_section_title field in the response JSON.",
        "value": {
            "strategy": "heading_section_paragraph",
            "input_type": "html",
            "chunk_min_words": 300,
            "chunk_overlap_words": 0,
            "code_behavior": "remove_code_sections",
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html,
        },
    },
    "example14": {
        "summary": "Example with table. Heading section sentence chunking HTML with chunk_min_words=250 and chunk_overlap_words=50.",
        "description": "We chunk the HTML string by sentences, keeping track of which heading section the sentence originated from. "
        "We add sentences until each chunk is at least 250 words if possible, with at least 50 words of overlap. "
        "Important distinction is it does not treat headings as paragraphs themselves. They are returned in the "
        "heading_section_title field in the response JSON.",
        "value": {
            "strategy": "heading_section_sentence",
            "input_type": "html",
            "chunk_min_words": 250,
            "chunk_overlap_words": 50,
            "additional_metadata": {
                "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios"
            },
            "input_str": example_html2,
        },
    },
}


for examples in [chunking_examples]:
    for k, v in examples.items():
        v[
            "description"
        ] = f'{v["description"]}\n\n**❗To run this example, click "Try it out", and then click "Execute".**'
