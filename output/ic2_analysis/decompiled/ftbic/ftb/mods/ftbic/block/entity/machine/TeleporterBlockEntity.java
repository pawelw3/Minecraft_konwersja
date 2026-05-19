package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBIC;
import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.util.TeleporterEntry;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Registry;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

public class TeleporterBlockEntity extends ElectricBlockEntity {
   public BlockPos linkedPos = null;
   public ResourceKey<Level> linkedDimension = null;
   public String linkedName = null;
   public int warmup = 0;
   public int cooldown = 0;
   public boolean isPublic = false;
   public String name = "";

   public TeleporterBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.TELEPORTER, pos, state);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      if (this.linkedPos != null && this.linkedDimension != null) {
         tag.m_128405_("LinkedX", this.linkedPos.m_123341_());
         tag.m_128405_("LinkedY", this.linkedPos.m_123342_());
         tag.m_128405_("LinkedZ", this.linkedPos.m_123343_());
         tag.m_128359_("LinkedDimension", this.linkedDimension.m_135782_().toString());
         tag.m_128359_("LinkedName", this.linkedName);
      }

      if (this.warmup > 0) {
         tag.m_128405_("Warmup", this.warmup);
      }

      if (this.cooldown > 0) {
         tag.m_128405_("Cooldown", this.cooldown);
      }

      if (this.isPublic) {
         tag.m_128379_("Public", true);
      }

      if (!this.name.isEmpty()) {
         tag.m_128359_("Name", this.name);
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.linkedPos = null;
      this.linkedDimension = null;
      this.linkedName = "";
      if (tag.m_128441_("LinkedDimension")) {
         this.linkedPos = new BlockPos(tag.m_128451_("LinkedX"), tag.m_128451_("LinkedY"), tag.m_128451_("LinkedZ"));
         this.linkedDimension = ResourceKey.m_135785_(Registry.f_122819_, new ResourceLocation(tag.m_128461_("LinkedDimension")));
         this.linkedName = tag.m_128461_("LinkedName");
      }

      this.warmup = tag.m_128451_("Warmup");
      this.cooldown = tag.m_128451_("Cooldown");
      this.isPublic = tag.m_128471_("Public");
      this.name = tag.m_128461_("Name");
   }

   @Override
   public void writeNetData(CompoundTag tag) {
      super.writeNetData(tag);
      if (this.linkedName != null && !this.linkedName.isEmpty()) {
         tag.m_128359_("LinkedName", this.linkedName);
      }
   }

   @Override
   public void readNetData(CompoundTag tag) {
      super.readNetData(tag);
      if (tag != null) {
         if (tag.m_128441_("LinkedName")) {
            this.linkedName = tag.m_128461_("LinkedName");
         }
      }
   }

   @Override
   public void stepOn(ServerPlayer player) {
      if (this.cooldown <= 0 && this.linkedDimension != null && this.linkedPos != null) {
         double use = this.getEnergyUse(this.linkedDimension, this.linkedPos);
         if (!(this.energy < use)) {
            ServerLevel linkedLevel = player.f_8924_.m_129880_(this.linkedDimension);
            if (linkedLevel == null || !linkedLevel.m_46749_(this.linkedPos)) {
               player.m_5661_(new TranslatableComponent("block.ftbic.teleporter.load_error").m_130940_(ChatFormatting.RED), true);
            } else if (this.warmup < 10) {
               this.warmup += 2;
            } else if (linkedLevel.m_7702_(this.linkedPos) instanceof TeleporterBlockEntity t) {
               Direction direction = t.getFacing(Direction.NORTH);
               this.energy -= use;
               player.m_8999_(
                  linkedLevel,
                  (double)this.linkedPos.m_123341_() + 0.5,
                  (double)this.linkedPos.m_123342_() + 1.1,
                  (double)this.linkedPos.m_123343_() + 0.5,
                  direction.m_122435_() + 90.0F,
                  0.0F
               );
               this.f_58857_
                  .m_6263_(
                     null,
                     (double)this.f_58858_.m_123341_() + 0.5,
                     (double)this.f_58858_.m_123342_() + 1.5,
                     (double)this.f_58858_.m_123343_() + 0.5,
                     SoundEvents.f_11852_,
                     SoundSource.NEUTRAL,
                     1.0F,
                     1.0F
                  );
               this.f_58857_.m_6263_(null, player.m_20185_(), player.m_20188_(), player.m_20189_(), SoundEvents.f_11852_, SoundSource.NEUTRAL, 1.0F, 1.0F);
               this.cooldown = 20;
               this.warmup = 0;
               this.m_6596_();
               t.cooldown = 60;
               t.m_6596_();
               if (this.linkedName != null && !this.linkedName.equals(t.name)) {
                  this.linkedName = t.name;
                  this.syncBlock();
               }

               FTBIC.LOGGER.debug(player.m_6302_() + " used teleporter to " + this.linkedDimension.m_135782_() + ":" + this.linkedPos);
            } else {
               this.linkedName = "";
               this.syncBlock();
            }
         }
      }
   }

   @Override
   public void tick() {
      if (this.cooldown > 0) {
         this.cooldown--;
      }

      if (this.warmup > 0) {
         this.warmup--;
      }

      if (this.cooldown <= 0
         && this.linkedDimension != null
         && this.linkedPos != null
         && this.energy >= this.getEnergyUse(this.linkedDimension, this.linkedPos)) {
         this.active = true;
      }

      super.tick();
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_() && !this.placerId.equals(player.m_142081_())) {
         player.m_5661_(new TranslatableComponent("block.ftbic.teleporter.perm_error").m_130940_(ChatFormatting.RED), true);
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public boolean savePlacer() {
      return true;
   }

   public double getEnergyUse(ResourceKey<Level> d, BlockPos p) {
      if (d != this.f_58857_.m_46472_()) {
         return (Double)FTBICConfig.MACHINES.TELEPORTER_MAX_USE.get();
      } else {
         double mind = (Double)FTBICConfig.MACHINES.TELEPORTER_MIN_DISTANCE.get();
         double maxd = (Double)FTBICConfig.MACHINES.TELEPORTER_MAX_DISTANCE.get();
         double dx = (double)(p.m_123341_() - this.f_58858_.m_123341_());
         double dz = (double)(p.m_123343_() - this.f_58858_.m_123343_());
         double dist = Mth.m_14008_(dx * dx + dz * dz, mind, maxd);
         return Mth.m_14139_(
            (dist - mind) / (maxd - mind), (Double)FTBICConfig.MACHINES.TELEPORTER_MIN_USE.get(), (Double)FTBICConfig.MACHINES.TELEPORTER_MAX_USE.get()
         );
      }
   }

   @Override
   public void writeMenu(ServerPlayer player, FriendlyByteBuf buf) {
      super.writeMenu(player, buf);
      List<TeleporterEntry> list = new ArrayList<>();
      buf.m_130130_(list.size());

      for (TeleporterEntry e : list) {
         e.write(buf);
      }
   }

   public void select(ServerPlayer player, ResourceKey<Level> d, BlockPos p) {
      if (this.placerId.equals(player.m_142081_())) {
         ServerLevel linkedLevel = player.f_8924_.m_129880_(d);
         if (linkedLevel != null && linkedLevel.m_46749_(p)) {
            if (linkedLevel.m_7702_(p) instanceof TeleporterBlockEntity t) {
               if (t.isPublic || t.placerId.equals(player.m_142081_())) {
                  this.linkedDimension = d;
                  this.linkedPos = p;
                  this.linkedName = t.name;
                  this.syncBlock();
               }
            } else {
               player.m_5661_(new TranslatableComponent("block.ftbic.teleporter.load_error").m_130940_(ChatFormatting.RED), true);
            }
         } else {
            player.m_5661_(new TranslatableComponent("block.ftbic.teleporter.load_error").m_130940_(ChatFormatting.RED), true);
         }
      } else {
         player.m_5661_(new TranslatableComponent("block.ftbic.teleporter.perm_error").m_130940_(ChatFormatting.RED), true);
      }
   }
}
