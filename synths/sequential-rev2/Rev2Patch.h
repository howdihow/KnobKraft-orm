/*
   Copyright (c) 2019 Christof Ruch. All rights reserved.

   Dual licensed: Distributed under Affero GPL license by default, an MIT license is available for purchase
*/

#pragma once

#include "Patch.h"
#include "Rev2ParamDefinition.h"

#include "LayeredPatch.h"

namespace midikraft {

	class Rev2PatchNumber : public PatchNumber {
	public:
		using PatchNumber::PatchNumber;
		virtual std::string friendlyName() const override;

	private:
		int bank_; // 0 to 7 for banks U1 to U4 and F1 to F4
	};

	class Rev2Patch : public Patch, public LayeredPatch {
	public:
		Rev2Patch();
		Rev2Patch(Synth::PatchData const &patchData);

		virtual std::string patchName() const override;
		virtual void setName(std::string const &name) override;
		virtual std::shared_ptr<PatchNumber> patchNumber() const override;
		virtual void setPatchNumber(MidiProgramNumber patchNumber) override;

		virtual std::vector<SynthParameterDefinition *> allParameterDefinitions() override;

		// Interface for layered Patches (for the Librarian)
		virtual LayerMode layerMode() const override;
		virtual int numberOfLayers() const override;
		virtual std::string layerName(int layerNo) const override;

		static std::shared_ptr<Rev2ParamDefinition> find(std::string const &paramID);

	private:
		Rev2PatchNumber number_;
	};

}

