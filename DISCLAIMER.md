# Disclaimer

This repository contains a **deliberately vulnerable** application and
**offensive security test code**, published for education and defensive research.

By using it you agree that:

1. **Lab-only.** The target (`target/`) exists to be attacked **by you, on
   infrastructure you own or are explicitly authorized to test.** Do not deploy
   it to a shared or public network — it is insecure on purpose.
2. **No third-party targets.** The attack code here is wired to the bundled
   target. Do not point it at any system you do not own or have written
   authorization to test. Unauthorized testing is illegal in most jurisdictions.
3. **Canary, not theft.** Every "finding" is demonstrated by a planted canary
   token leaking — not by exfiltrating real data. Keep it that way.
4. **No warranty.** Provided "as is", without warranty of any kind. The author is
   not liable for misuse.

If you want to attack a real model, use the optional local `ollama` backend
against a model on your own machine.
