package com.maciej916.indreb.common.entity.block;

import com.maciej916.indreb.common.enums.UpgradeType;
import com.maciej916.indreb.common.item.impl.upgrade.ItemUpgrade;
import java.util.List;
import javax.annotation.Nonnull;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.SlotItemHandler;

public class UpgradeSlotHandler extends SlotItemHandler {
   private final List<UpgradeType> acceptedUpgrades;

   public UpgradeSlotHandler(IItemHandler itemHandler, int index, int xPosition, int yPosition, List<UpgradeType> acceptedUpgrades) {
      super(itemHandler, index, xPosition, yPosition);
      this.acceptedUpgrades = acceptedUpgrades;
   }

   public boolean m_5857_(@Nonnull ItemStack stack) {
      return stack.m_41720_() instanceof ItemUpgrade itemUpgrade ? this.acceptedUpgrades.contains(itemUpgrade.getUpgradeType()) : false;
   }

   public List<UpgradeType> getAcceptedUpgrades() {
      return this.acceptedUpgrades;
   }
}
