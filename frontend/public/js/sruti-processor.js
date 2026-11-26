// frontend/public/js/sruti-processor.js
// AudioWorkletProcessor: 22-sruti oscillator + multi-harmonic tanpura drone
// Supports:
//   - Note mode ('play' / 'stop'): exponential mind glide + kampa + 2nd harmonic
//   - Drone mode ('startDrone' / 'setDroneGain' / 'stopDrone'): multi-harmonic Sa/Pa/Sa' bed

class SrutiOscillator extends AudioWorkletProcessor {
  constructor() {
    super();
    // Note state
    this._phase = 0;
    this._freq = 240.0;
    this._startFreq = 240.0;
    this._endFreq = 240.0;
    this._targetGain = 0.0;
    this._currentGain = 0.0;
    this._active = false;
    this._samplesRemaining = 0;
    this._totalSamples = 0;
    this._kampaHz = 0;
    this._kampaDepthHz = 0;
    this._kampaPhase = 0;

    // Multi-harmonic tanpura drone state (mandrā Pa, Sa, Pa, Sa' + harmonics)
    this._droneActive = false;
    this._droneTargetGain = 0.0;
    this._droneCurrentGain = 0.0;
    this._droneSaHz = 240.0;
    this._dronePhaseMandPa = 0;
    this._dronePhaseSa = 0;
    this._dronePhaseSa2 = 0;
    this._dronePhaseSa3 = 0;
    this._dronePhasePa = 0;
    this._dronePhasePa2 = 0;
    this._dronePhaseHighSa = 0;
    this._droneModPhase = 0;

    this.port.onmessage = (event) => {
      const msg = event.data || {};
      if (msg.type === 'play') {
        this._startFreq = msg.freq;
        this._endFreq = (typeof msg.endFreq === 'number') ? msg.endFreq : msg.freq;
        this._freq = this._startFreq;
        this._totalSamples = Math.max(1, Math.floor(msg.durationMs * sampleRate / 1000));
        this._samplesRemaining = this._totalSamples;
        this._targetGain = msg.gain ?? 0.15;
        this._active = true;
        this._kampaHz = msg.kampaHz ?? 0;
        const cents = msg.kampaDepthCents ?? 0;
        this._kampaDepthHz = cents > 0
          ? this._startFreq * (Math.pow(2, cents / 1200) - 1)
          : 0;
        this._kampaPhase = 0;
      } else if (msg.type === 'stop') {
        this._targetGain = 0.0;
        this._active = false;
      } else if (msg.type === 'startDrone') {
        this._droneSaHz = (typeof msg.saHz === 'number' && msg.saHz > 0) ? msg.saHz : 240.0;
        this._droneTargetGain = (typeof msg.gain === 'number') ? Math.max(0, msg.gain) : 0.08;
        this._droneActive = true;
      } else if (msg.type === 'setDroneGain') {
        if (typeof msg.saHz === 'number' && msg.saHz > 0) {
          this._droneSaHz = msg.saHz;
        }
        const g = (typeof msg.gain === 'number') ? Math.max(0, msg.gain) : 0.0;
        this._droneTargetGain = g;
        this._droneActive = g > 0;
      } else if (msg.type === 'stopDrone') {
        this._droneTargetGain = 0.0;
        this._droneActive = false;
      }
    };
  }

  _wrapPhase(phase) {
    const twoPi = 2 * Math.PI;
    if (phase > twoPi || phase < -twoPi) {
      phase = phase % twoPi;
    }
    if (phase < 0) phase += twoPi;
    return phase;
  }

  _renderDroneSample() {
    const fadePerSample = 1 / (0.02 * sampleRate); // 20ms smooth drone fade
    if (this._droneCurrentGain < this._droneTargetGain) {
      this._droneCurrentGain = Math.min(this._droneCurrentGain + fadePerSample, this._droneTargetGain);
    } else if (this._droneCurrentGain > this._droneTargetGain) {
      this._droneCurrentGain = Math.max(this._droneCurrentGain - fadePerSample, this._droneTargetGain);
    }

    if (this._droneCurrentGain <= 1e-6) {
      return 0.0;
    }

    // Subtle organic breathing (~0.12 Hz)
    this._droneModPhase = this._wrapPhase(this._droneModPhase + (2 * Math.PI * 0.12) / sampleRate);
    const shimmer = 1.0 + 0.04 * Math.sin(this._droneModPhase);

    const sa = this._droneSaHz;
    const mandPa = sa * 0.75;      // 3/4 mandrā Pa
    const pa = sa * 1.5;        // 3/2 Pa
    const highSa = sa * 2.0;    // 2/1 tāra Sa

    const sMandPa = 0.28 * Math.sin(this._dronePhaseMandPa);
    const sSa1 = 1.00 * Math.sin(this._dronePhaseSa);
    const sSa2 = 0.14 * Math.sin(this._dronePhaseSa2);
    const sSa3 = 0.06 * Math.sin(this._dronePhaseSa3);
    const sPa1 = 0.38 * Math.sin(this._dronePhasePa);
    const sPa2 = 0.05 * Math.sin(this._dronePhasePa2);
    const sHighSa = 0.22 * Math.sin(this._dronePhaseHighSa);

    this._dronePhaseMandPa = this._wrapPhase(this._dronePhaseMandPa + (2 * Math.PI * mandPa) / sampleRate);
    this._dronePhaseSa = this._wrapPhase(this._dronePhaseSa + (2 * Math.PI * sa) / sampleRate);
    this._dronePhaseSa2 = this._wrapPhase(this._dronePhaseSa2 + (2 * Math.PI * (sa * 2.0)) / sampleRate);
    this._dronePhaseSa3 = this._wrapPhase(this._dronePhaseSa3 + (2 * Math.PI * (sa * 3.0)) / sampleRate);
    this._dronePhasePa = this._wrapPhase(this._dronePhasePa + (2 * Math.PI * pa) / sampleRate);
    this._dronePhasePa2 = this._wrapPhase(this._dronePhasePa2 + (2 * Math.PI * (pa * 2.0)) / sampleRate);
    this._dronePhaseHighSa = this._wrapPhase(this._dronePhaseHighSa + (2 * Math.PI * highSa) / sampleRate);

    const mix = (sMandPa + sSa1 + sSa2 + sSa3 + sPa1 + sPa2 + sHighSa) * 0.42 * shimmer;
    return mix * this._droneCurrentGain;
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

      // Glide + kampa: per-sample instantaneous frequency
      const elapsed = this._totalSamples - this._samplesRemaining + i;
      const glideT = Math.min(1, elapsed / Math.max(1, this._totalSamples));
      const baseFreq =
        this._startFreq > 0 && this._endFreq > 0 && this._startFreq !== this._endFreq
          ? this._startFreq * Math.pow(this._endFreq / this._startFreq, glideT)
          : this._startFreq;
      let instFreq = baseFreq;
      if (this._kampaHz > 0 && this._kampaDepthHz > 0) {
        this._kampaPhase += (2 * Math.PI * this._kampaHz) / sampleRate;
        if (this._kampaPhase > 2 * Math.PI) this._kampaPhase -= 2 * Math.PI;
        instFreq = baseFreq + this._kampaDepthHz * Math.sin(this._kampaPhase);
      }
      this._freq = instFreq;

      // Fundamental + second harmonic (gentle, ~10% amplitude)
      const fundamental = Math.sin(this._phase);
      const secondHarm = 0.1 * Math.sin(2 * this._phase);
      const noteSample = (fundamental + secondHarm) * this._currentGain;
      const droneSample = this._renderDroneSample();

      channel[i] = noteSample + droneSample;

      // Advance phase
      this._phase = this._wrapPhase(this._phase + (2 * Math.PI * this._freq) / sampleRate);

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
