package dev.ftb.mods.ftbic.block.entity.generator;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.screen.SolarPanelMenu;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

public class SolarPanelBlockEntity extends GeneratorBlockEntity {
   public SolarPanelBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super(type, pos, state);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.maxEnergyOutputTransfer = Math.max((Double)FTBICConfig.ENERGY.LV_TRANSFER_RATE.get(), this.maxEnergyOutput);
   }

   @Override
   public void handleGeneration() {
      if (this.energy < this.energyCapacity && this.f_58857_.m_46461_() && this.f_58857_.m_45527_(this.f_58858_.m_7494_())) {
         this.energy = this.energy + Math.min(this.energyCapacity - this.energy, this.maxEnergyOutput);
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         this.openMenu((ServerPlayer)player, (id, inventory) -> new SolarPanelMenu(id, inventory, this));
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addShort(SyncedData.BAR, () -> this.f_58857_.m_46461_() && this.f_58857_.m_45527_(this.f_58858_.m_7494_()) ? 14 : 0);
   }
}
