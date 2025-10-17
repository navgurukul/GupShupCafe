import { ZoeSTT } from "@zoe-ng/stt";

const stt = new ZoeSTT();
stt.onPartial((t) => console.log("Partial:", t));
stt.onFinal((t) => console.log("Final:", t));
stt.start();