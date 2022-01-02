/*
   Copyright (c) 2022 Christof Ruch. All rights reserved.

   Dual licensed: Distributed under Affero GPL license by default, an MIT license is available for purchase
*/

#include "VerticalPatchButtonList.h"

#include "PatchHolderButton.h"
#include "LayoutConstants.h"

class PatchButtonRow: public Component {
public:
	PatchButtonRow(std::function<void(int)> clickHandler) : clickHandler_(clickHandler) {
	}

	virtual void resized() override {
		auto area = getLocalBounds();
		if (button_)
			button_->setBounds(area);
	}

	void setRow(int rowNo, midikraft::PatchHolder const &patch) {
		// This changes the row to be displayed with this component (reusing components within a list box)
		if (!button_) {
			button_ = std::make_unique<PatchHolderButton>(rowNo, false, clickHandler_);
			addAndMakeVisible(*button_);
			resized();
		}
		thePatch_ = patch; // Need a copy to keep the pointer alive
		button_->setPatchHolder(&thePatch_, false, false);
	}

	void clearRow() {
		if (button_) {
			button_.reset();
		}
	}

private:
	std::unique_ptr<PatchHolderButton> button_;
	std::function<void(int)> clickHandler_;
	midikraft::PatchHolder thePatch_;
};


class PatchListModel : public ListBoxModel {
public:
	PatchListModel(std::vector<midikraft::PatchHolder> const &patches, std::function<void(int)> onRowSelected) : patches_(patches), onRowSelected_(onRowSelected) {
	}

	int getNumRows() override
	{
		return (int) patches_.size();
	}

	void paintListBoxItem(int rowNumber, Graphics& g, int width, int height, bool rowIsSelected) override
	{
		ignoreUnused(rowNumber, width, height, rowIsSelected);
		g.fillAll();
	}

	Component* refreshComponentForRow(int rowNumber, bool isRowSelected, Component* existingComponentToUpdate) override
	{
		ignoreUnused(isRowSelected);
		if (rowNumber < getNumRows()) {
			if (existingComponentToUpdate) {
				auto existing = dynamic_cast<PatchButtonRow*>(existingComponentToUpdate);
				if (existing) {
					existing->setRow(rowNumber, patches_[rowNumber]);
					return existing;
				}
				throw std::runtime_error("This was not the correct row type, can't continue");
			}
			auto newComponent = new PatchButtonRow(onRowSelected_);
			newComponent->setRow(rowNumber, patches_[rowNumber]);
			return newComponent;
		}
		else {
			if (existingComponentToUpdate) {
				auto existing = dynamic_cast<PatchButtonRow*>(existingComponentToUpdate);
				if (existing) {
					existing->clearRow();
					return existing;
				}
				throw std::runtime_error("This was not the correct row type, can't continue");
			}
			return nullptr;
		}
	}

	

private:
	std::vector<midikraft::PatchHolder> patches_;
	std::function<void(int)> onRowSelected_;
};


VerticalPatchButtonList::VerticalPatchButtonList(bool isDropTarget)
{
	addAndMakeVisible(list_);
	list_.setRowHeight(LAYOUT_LARGE_LINE_SPACING);
}

void VerticalPatchButtonList::resized()
{
	auto bounds = getLocalBounds();
	list_.setBounds(bounds);
}

void VerticalPatchButtonList::setPatches(std::vector<midikraft::PatchHolder> const& patches)
{
	list_.setModel(new PatchListModel(patches, [this](int row) {
		SimpleLogger::instance()->postMessage("Row " + String(row) + "selected");
	}));
}
