// frontend/public/js/sruti-processor.js
// AudioWorkletProcessor: 22-śruti oscillator
// Receives frequency + duration from the main thread, synthesizes a sine wave
// with a subtle second harmonic for a musical (tanpura-like) timbre.

class SrutiOscillator extends AudioWorkletProcessor {
  constructor() {
    super();
    this._phase = 0;
    this._freq = 240.0;
    this._targetGain = 0.0;
    this._currentGain = 0.0;
    this._active = false;
    this._samplesRemaining = 0;

    this.port.onmessage = (event) => {
      const msg = event.data;
      if (msg.type === 'play') {
        this._freq = msg.freq;
        this._samplesRemaining = Math.floor(msg.durationMs * sampleRate / 1000);
        this._targetGain = msg.gain ?? 0.15;
        this._active = true;
      } else if (msg.type === 'stop') {
        this._targetGain = 0.0;
      }
    };
  }

  process(inputs, outputs) {
    const output = outputs[0];
    if (!output || !output[0]) return true;
    const channel = output[0];

    // Gain smoothing: avoid clicks (5ms fade in/out)
    const fadePerSample = 1 / (0.005 * sampleRate);

    for (let i = 0; i < channel.length; i++) {
      if (this._currentGain < this._targetGain) {
        this._currentGain = Math.min(this._currentGain + fadePerSample, this._targetGain);
      } else if (this._currentGain > this._targetGain) {
        this._currentGain = Math.max(this._currentGain - fadePerSample, this._targetGain);
      }

      // Fundamental + second harmonic (gentle, ~10% amplitude)
      const fundamental = Math.sin(this._phase);
      const secondHarm = 0.1 * Math.sin(2 * this._phase);
      const sample = (fundamental + secondHarm) * this._currentGain;

      channel[i] = sample;

      // Advance phase
      this._phase += 2 * Math.PI * this._freq / sampleRate;
      if (this._phase > 2 * Math.PI) this._phase -= 2 * Math.PI;

      // Countdown timer
      if (this._active) {
        this._samplesRemaining--;
        if (this._samplesRemaining <= 0) {
          this._targetGain = 0.0;
          this._active = false;
        }
      }
    }

    return true;
  }
}

registerProcessor('sruti-oscillator', SrutiOscillator);